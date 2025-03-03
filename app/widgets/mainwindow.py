import os
import xml.etree.ElementTree as ET

from PySide6.QtCore import QSettings, Qt, QTimer, QCoreApplication
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QMainWindow
from rssdk import RsPoe

from app.bitinterface import BitInterface, ErrorSeverity, PluginStatus
from app.ui.ui_mainwindow import Ui_MainWindow
from app.widgets.poe_widget import PoeWidget


class MainWindow(QMainWindow):
    MIN_PASSING_VOLTAGE = 50
    MIN_PASSING_CURRENT = 1
    MIN_PASSING_POWER = 20

    _ports: dict[int, PoeWidget] = {}
    _poe = RsPoe()
    _bit_interface: BitInterface | None  = None

    def __init__(self, args: list[str]) -> None:
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        if args and args[0].startswith("BIT_PLUGIN_INT"):
            self._bit_interface = BitInterface(args[0], "PoE Tester")
            self._bit_interface.set_status(PluginStatus.PLUGIN_STARTUP, "Starting")
            self._bit_interface.set_error(ErrorSeverity.ERRORNONE, f"Using the following thresholds: {self.MIN_PASSING_VOLTAGE}V, {self.MIN_PASSING_CURRENT}A, {self.MIN_PASSING_POWER}W")

        self._timer = QTimer(interval=1000, parent=self)
        self._timer.timeout.connect(self._update_ports)

        window_title = f"{QApplication.applicationDisplayName()} - {QApplication.applicationVersion()}"
        self.setWindowTitle(window_title)

        # Ensure we start in the correct state
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.continue_button.setEnabled(False) # Force user to select an item

        # Enable start button after user selects a valid device
        self.ui.device_combobox.currentIndexChanged.connect(self._device_combobox_selection_changed)
        self.ui.continue_button.clicked.connect(self._continue_clicked)

        if self.is_frozen():
            device_file_path = os.path.join(QCoreApplication.applicationDirPath(), "devices")
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
                    if isinstance(poe_element, ET.Element) and poe_element.findall("port"):
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
        self._ports.clear()
        while self.ui.poe_ports_layout.count():
            child = self.ui.poe_ports_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        device_file = self.ui.device_combobox.currentData(role=Qt.ItemDataRole.UserRole)
        self._poe.setXmlFile(device_file)
        index = 0
        for port in self._poe.getPortList():
            row = int(index & 0b1)
            col = int(index / 2)
            widget = PoeWidget(port, self)
            self._ports[port] = widget
            self.ui.poe_ports_layout.addWidget(widget, row, col, Qt.AlignmentFlag.AlignCenter)
            index += 1

        
        self._poe.setXmlFile(device_file)
        self._timer.start()
        self.ui.stackedWidget.setCurrentIndex(1)
        self._update_ports()

    def _update_ports(self) -> None:
        for port, widget in self._ports.items():
            widget.voltage = self._poe.getPortVoltage(port)
            widget.current = self._poe.getPortCurrent(port)
            widget.power = self._poe.getPortPower(port)

    def _load_settings(self) -> None:
        settings = QSettings()
        self.restoreGeometry(settings.value("geometry"))
        self.restoreState(settings.value("state"))

    def _save_settings(self) -> None:
        settings = QSettings()
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("state", self.saveState())

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._bit_interface:
            failed_ports = []
            for port, widget in self._ports.items():
                v = widget.max_voltage
                c = widget.max_current
                p = widget.max_power
                self._bit_interface.set_error(ErrorSeverity.ERRORNONE, f"LAN {port}: Voltage: {v:.2f}V, Current: {c:.2f}A, Power: {p:.2f}W")

                if v < self.MIN_PASSING_VOLTAGE or c < self.MIN_PASSING_CURRENT or p < self.MIN_PASSING_POWER:
                    failed_ports.append(port)

            self._bit_interface.set_error(ErrorSeverity.ERRORCRITICAL, f"LAN(s) {", ".join(map(str, failed_ports))} below threshold", wait=True)
            self._bit_interface.cycle += 1
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
        return getattr(sys, 'frozen', False)
