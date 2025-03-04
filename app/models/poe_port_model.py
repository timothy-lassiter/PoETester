from PySide6.QtCore import QObject, Signal


class PoePortModel(QObject):
    voltage_changed = Signal(int, float)
    max_voltage_changed = Signal(int, float)
    current_changed = Signal(int, float)
    max_current_changed = Signal(int, float)
    power_changed = Signal(int, float)
    max_power_changed = Signal(int, float)
    value_changed = Signal(int)

    _voltage = 0.0
    _voltage_max = 0.0

    _current = 0.0
    _current_max = 0.0

    _power = 0.0
    _power_max = 0.0

    def __init__(self, id: int) -> None:
        super().__init__()
        self._id = id
        self.voltage_changed.connect(self.value_changed)
        self.max_voltage_changed.connect(self.value_changed)
        self.current_changed.connect(self.value_changed)
        self.max_current_changed.connect(self.value_changed)
        self.power_changed.connect(self.value_changed)
        self.max_power_changed.connect(self.value_changed)

    @property
    def id(self) -> int:
        return self._id

    @property
    def voltage(self) -> float:
        return self._voltage

    @voltage.setter
    def voltage(self, value: float) -> None:
        if self._voltage != value:
            self._voltage = value
            self.voltage_changed.emit(self.id, value)
        
        if self._voltage_max < value:
            self._voltage_max = value
            self.max_voltage_changed.emit(self.id, value)
        

    @property
    def max_voltage(self) -> float:
        return self._voltage_max

    @property
    def current(self) -> float:
        return self._current

    @current.setter
    def current(self, value: float) -> None:
        if self._current != value:
            self._current = value
            self.current_changed.emit(self.id, value)

        if self._current_max < value:
            self._current_max = value
            self.max_current_changed.emit(self.id, value)

    @property
    def max_current(self) -> float:
        return self._current_max

    @property
    def power(self) -> float:
        return self._power

    @power.setter
    def power(self, value: float) -> None:
        if self._power != value:
            self._power = value
            self.power_changed.emit(self.id, value)
        
        if self._power_max < value:
            self._power_max = value
            self.max_power_changed.emit(self.id, value)

    @property
    def max_power(self) -> float:
        return self._power_max
