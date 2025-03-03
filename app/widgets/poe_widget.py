import xml.etree.ElementTree as ET

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QFrame

from app.ui.ui_poe_widget import Ui_PoeWidget

from rssdk import PoeState


class PoeWidget(QFrame):
    _voltage = 0.0
    _voltage_max = 0.0

    _current = 0.0
    _current_max = 0.0

    _power = 0.0
    _power_max = 0.0

    def __init__(self, id: int, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)

        self.ui = Ui_PoeWidget()
        self.ui.setupUi(self)

        self.ui.lan_id_label.setText(f"LAN {id}")

    @property
    def voltage(self) -> float:
        return self._voltage
        
    @voltage.setter
    def voltage(self, value: float) -> None:
        self._voltage = value
        self._voltage_max = max(self._voltage_max, value)

        self.ui.voltage_value.setText(f"{value:.2f}V")
        self.ui.voltage_max.setText(f"{self._voltage_max:.2f}V")

    @property
    def max_voltage(self) -> float:
        return self._voltage_max

    @property
    def current(self) -> float:
        return self._current
        
    @current.setter
    def current(self, value: float) -> None:
        self._current = value
        self._current_max = max(self._current_max, value)

        self.ui.current_value.setText(f"{value:.2f}A")
        self.ui.current_max.setText(f"{self._current_max:.2f}A")

    @property
    def max_current(self) -> float:
        return self._current_max

    @property
    def power(self) -> float:
        return self._power
        
    @power.setter
    def power(self, value: float) -> None:
        self._power = value
        self._power_max = max(self._power_max, value)

        self.ui.power_value.setText(f"{value:.2f}W")
        self.ui.power_max.setText(f"{self._power_max:.2f}W")

    @property
    def max_power(self) -> float:
        return self._power_max
