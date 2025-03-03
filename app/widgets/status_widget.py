from PySide6.QtCore import Qt, QRectF, QSize
from PySide6.QtGui import QColor, QPainter, QPen, QBrush
from PySide6.QtWidgets import QWidget


class StatusIndicator(QWidget):
    """
    A simple round status indicator widget.

    The indicator's color can be changed to represent different states.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color: QColor = QColor(Qt.gray)  # Default color: gray
        self._border_color: QColor = QColor(Qt.black)
        self._border_width: int = 2
        self.setFixedSize(24, 24)  # Default size
        self.setSizePolicy(self.sizePolicy().horizontalPolicy(), self.sizePolicy().verticalPolicy())

    def set_color(self, color: QColor | str) -> None:
        """Sets the indicator color."""
        if isinstance(color, str):
            color = QColor(color)
        self._color = color
        self.update()  # Force a repaint

    def get_color(self) -> QColor:
        return self._color
    
    def set_border_color(self, color: QColor | str) -> None:
      if isinstance(color, str):
        color = QColor(color)
      self._border_color = color
      self.update()

    def set_border_width(self, width: int) -> None:
      self._border_width = width
      self.update()
    
    def set_size(self, size: int) -> None:
      self.setFixedSize(size, size)
      self.update()

    def paintEvent(self, event) -> None:
        """Paints the round indicator."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate the rectangle for the circle
        rect = QRectF(0, 0, self.width(), self.height())
        
        #calculate the offset from the rectangle edge for drawing the circle
        offset = self._border_width / 2
        circle_rect = QRectF(rect.x() + offset, rect.y() + offset, rect.width() - (offset * 2), rect.height() - (offset * 2))

        # Draw border
        pen = QPen(self._border_color)
        pen.setWidth(self._border_width)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(circle_rect)

        # Draw indicator
        painter.setPen(Qt.NoPen)  # No outline for the fill
        painter.setBrush(QBrush(self._color))
        painter.drawEllipse(circle_rect)
    
    def sizeHint(self) -> QSize:
      return QSize(24, 24)

