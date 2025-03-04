import os
import xml.etree.ElementTree as ET

from PySide6.QtCore import QSettings, Qt, QTimer, QCoreApplication
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QMainWindow
from rssdk import RsPoe

from app.bitinterface import BitInterface, ErrorSeverity, PluginStatus
from app.ui.ui_mainwindow import Ui_MainWindow
from app.models.poe_port_model import PoePortModel
from app.models.poe_table_model import PoeTableModel


class MainWindow(QMainWindow):
    _poe = RsPoe()
    _bit_interface: BitInterface | None = None
    _last_port_updated: int = 0

    def __init__(self, args: list[str]) -> None:
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._poe_table_model = PoeTableModel()
        self.ui.poe_table_view.setModel(self._poe_table_model)

        if args and args[0].startswith("BIT_PLUGIN_INT"):
            self._bit_interface = BitInterface(args[0], "PoE Tester")
            # We only use the read and verify operations
            self._bit_interface.read_operations = 0
            self._bit_interface.verify_operations = 0
            self._bit_interface.set_status(PluginStatus.PLUGIN_STARTUP, "Starting")

        self._timer = QTimer(interval=10, parent=self)
        self._timer.timeout.connect(self._update_ports)

        window_title = f"{QApplication.applicationDisplayName()} - {QApplication.applicationVersion()}"
        self.setWindowTitle(window_title)

        # Ensure we start in the correct state
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.continue_button.setEnabled(False)  # Force user to select an item

        # Enable start button after user selects a valid device
        self.ui.device_combobox.currentIndexChanged.connect(
            self._device_combobox_selection_changed
        )
        self.ui.continue_button.clicked.connect(self._continue_clicked)

        if self.is_frozen():
            device_file_path = os.path.join(
                QCoreApplication.applicationDirPath(), "devices"
            )
        else:
            device_file_path = "devices"

        for filename in os.listdir(device_file_path):
            filepath = os.path.join(device_file_path, filename)

            try:
                tree = ET.parse(filepath)
                root = tree.getroot()
                if root.tag == "computer":
                    computer_name = root.attrib.get("id")
                    poe_element = root.find("poe_controller")
                    if isinstance(poe_element, ET.Element) and poe_element.findall(
                        "port"
                    ):
                        name = computer_name or filename
                        self.ui.device_combobox.addItem(name.upper(), filepath)

            except FileNotFoundError:
                pass
            except ET.ParseError:
                pass

        self._load_settings()

    def _device_combobox_selection_changed(self, index: int) -> None:
        self.ui.continue_button.setEnabled(index != 0)

    def _continue_clicked(self) -> None:
        self.ui.continue_button.setEnabled(False)
        self._poe_table_model.passing_power = self.ui.passing_power_input.value()
        self._poe_table_model.passing_voltage = self.ui.passing_voltage_input.value()

        if self._bit_interface:
            self._bit_interface.set_error(
                ErrorSeverity.ERRORNONE,
                f"Using the following thresholds: {self._poe_table_model.passing_voltage:.2f}V, {self._poe_table_model.passing_power:.2f}W",
            )

        device_file = self.ui.device_combobox.currentData(role=Qt.ItemDataRole.UserRole)
        self._poe.setXmlFile(device_file)

        for port in self._poe.getPortList():
            if port == 255:
                continue

            port_model = PoePortModel(port)
            self._poe_table_model.addPort(port_model)

        self._timer.start()
        self.ui.stackedWidget.setCurrentWidget(self.ui.poe_table_page)
        self._update_ports()

    def _update_ports(self) -> None:
        if self._last_port_updated >= len(self._poe_table_model.ports):
            self._last_port_updated = 0

        port_model = self._poe_table_model.ports[self._last_port_updated]
        port_model.voltage = self._poe.getPortVoltage(port_model.id)
        QCoreApplication.processEvents()
        if port_model.voltage >= self._poe_table_model.passing_voltage:
            port_model.power = self._poe.getPortPower(port_model.id)
            QCoreApplication.processEvents()

        if self._bit_interface:
            self._bit_interface.cycle += 1
            self._bit_interface.read_operations += 1
            self._bit_interface.verify_operations += 1


            all_passing = True
            for port_model in self._poe_table_model.ports:
                if not self._poe_table_model.is_port_passing(port_model.id):
                    all_passing = False
                    break

            if all_passing:
                self.close()

        self._last_port_updated += 1

    def _load_settings(self) -> None:
        settings = QSettings()
        self.restoreGeometry(settings.value("geometry"))
        self.restoreState(settings.value("state"))

        passing_voltage = settings.value("passing_voltage")
        passing_power = settings.value("passing_power")

        if isinstance(passing_voltage, (float, str)):
            self._poe_table_model.passing_voltage = float(passing_voltage)
        if isinstance(passing_power, (float, str)):
            self._poe_table_model.passing_power = float(passing_power)

        self.ui.passing_voltage_input.setValue(self._poe_table_model.passing_voltage)
        self.ui.passing_power_input.setValue(self._poe_table_model.passing_power)

    def _save_settings(self) -> None:
        settings = QSettings()
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("state", self.saveState())
        settings.setValue("passing_voltage", self._poe_table_model.passing_voltage)
        settings.setValue("passing_power", self._poe_table_model.passing_power)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._bit_interface:
            failed_ports = []
            for port_model in self._poe_table_model.ports:
                v = port_model.max_voltage
                c = port_model.max_current
                p = port_model.max_power
                self._bit_interface.set_error(
                    ErrorSeverity.ERRORNONE,
                    f"LAN {port_model.id}: Voltage: {v:.2f}V, Current: {c:.2f}A, Power: {p:.2f}W",
                    wait=True,
                )

                if not self._poe_table_model.is_port_passing(port_model.id):
                    failed_ports.append(port_model.id)

            if failed_ports:
                self._bit_interface.set_error(
                    ErrorSeverity.ERRORCRITICAL,
                    f"LAN(s) {", ".join(map(str, failed_ports))} below threshold",
                    wait=True,
                )

            self._bit_interface.set_pretest_complete(wait=True)

        self._save_settings()
        return super().closeEvent(event)

    def is_frozen(self) -> bool:
        """
        Checks if the current application is running as a compiled executable (e.g., using cx_Freeze).

        Returns:
            bool: True if running as a compiled executable, False otherwise.
        """
        import sys

        return getattr(sys, "frozen", False)
