from PySide6.QtGui import Qt, QMouseEvent
from PySide6.QtWidgets import QSlider

class MediaSlider(QSlider):
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # Grab pixel user clicked on
            click_position = event.position().x()
            # Grab width of slider
            total_width = self.width()
            # Assuming a position of 100px and a width of 400px
            # Grab percentage (100th pixel / 400px width = 0.25)
            percentage = click_position / total_width

            # New value is minimum (0) + ((maximum (400px) - minimum (0px)) * percentage (0.25))
            new_value = self.minimum() + ((self.maximum() - self.minimum()) * percentage)

            # Value is new value converted from a float to an int
            self.setValue(int(new_value))

            # Hey Engine, the Slider moved!
            self.sliderMoved.emit(int(new_value))

            event.accept()
        super().mousePressEvent(event)