from PySide6.QtWidgets import QWidget, QFrame

from app.models.poe_port_model import PoePortModel
from app.ui.ui_poe_widget import Ui_PoeWidget




class PoeWidget(QFrame):
    def __init__(self, model: PoePortModel, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)

        self.ui = Ui_PoeWidget()
        self.ui.setupUi(self)

        self._model = model
        self._model.voltage_changed.connect(self._voltage_changed)
        self._model.max_voltage_changed.connect(self._max_voltage_changed)

        self._model.current_changed.connect(self._current_changed)
        self._model.max_current_changed.connect(self._max_current_changed)

        self._model.power_changed.connect(self._power_changed)
        self._model.max_power_changed.connect(self._max_power_changed)

        self.ui.lan_id_label.setText(f"LAN {model.id}")

    def _voltage_changed(self) -> None:
        self.ui.voltage_label.setText(f"{self._model.voltage:.2f}V")

    def _max_voltage_changed(self) -> None:
        self.ui.voltage_max.setText(f"{self._model.max_voltage:.2f}V")

    def _current_changed(self) -> None:
        self.ui.current_label.setText(f"{self._model.current:.2f}A")

    def _max_current_changed(self) -> None:
        self.ui.current_max.setText(f"{self._model.max_current:.2f}A")

    def _power_changed(self) -> None:
        self.ui.power_label.setText(f"{self._model.power:.2f}W")

    def _max_power_changed(self) -> None:
        self.ui.power_max.setText(f"{self._model.max_power:.2f}W")