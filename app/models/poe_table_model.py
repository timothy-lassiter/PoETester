import typing
from PySide6.QtCore import QAbstractTableModel, QObject, Qt, QModelIndex, QPersistentModelIndex
from PySide6.QtGui import QColor

from .poe_port_model import PoePortModel

class PoeTableModel(QAbstractTableModel):
    passing_voltage: float = 48
    passing_power: float = 4.5

    def __init__(self, /, parent: QObject | None = None):
        super().__init__(parent)
        self._data: dict[int, PoePortModel] = {}

    @property
    def ports(self) -> list[PoePortModel]:
        return list(self._data.values())

    def data(self, index: QModelIndex | QPersistentModelIndex, /, role: int = Qt.ItemDataRole.DisplayRole) -> typing.Any:

        col = index.column()
        row = index.row()
        port_model = self.ports[row]

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return f"{port_model.voltage:.2f}V"
            elif col == 1:
                return f"{port_model.max_voltage:.2f}V"
            elif col == 2:
                return f"{port_model.current:.2f}A"
            elif col == 3:
                return f"{port_model.max_current:.2f}A"
            elif col == 4:
                return f"{port_model.power:.2f}W"
            elif col == 5:
                return f"{port_model.max_power:.2f}W"  
        elif role == Qt.ItemDataRole.BackgroundRole:
            if self.is_port_passing(port_model.id):
                return QColor(Qt.GlobalColor.green)
            else:
                return QColor(Qt.GlobalColor.red)
    
    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return len(self._data)
    
    def columnCount(self, /, parent: QModelIndex | QPersistentModelIndex = QModelIndex()):
        return 6
    
    def headerData(self, section, orientation, /, role = ...):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if section == 0:
                    return "Voltage"
                elif section ==1:
                    return "Max Voltage"
                elif section == 2:
                    return "Current"
                elif section == 3:
                    return "Max Current"
                elif section == 4:
                    return "Power"
                elif section == 5:
                    return "Max Power"
            elif orientation == Qt.Orientation.Vertical:
                return f"LAN {self.ports[section].id}"
    
    def addPort(self, port: PoePortModel):
        self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
        self._data[port.id] = port
        self.endInsertRows()
        port.value_changed.connect(self._on_port_changed)

    def getPort(self, port_id: int) -> PoePortModel:
        return self._data[port_id]
    
    def is_port_passing(self, port_id: int) -> bool:
        port_model = self.getPort(port_id)
        return port_model.max_voltage >= self.passing_voltage and port_model.max_power >= self.passing_power

    def _on_port_changed(self, port_id: int):
        try:
            row = next(i for i, id in enumerate(self._data) if id == port_id)
        except StopIteration:
            print("Warning: Port not found when attempting to update the table view.")
            return
        
        # Create QModelIndex instances for the top-left and bottom-right of the row.
        top_left = self.index(row, 0)
        bottom_right = self.index(row, self.columnCount() - 1)

        # Emit the dataChanged signal for the entire row
        self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])
