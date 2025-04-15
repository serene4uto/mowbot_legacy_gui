
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)

class SettingsPanelView(QWidget):
    def __init__(self):
        super().__init__()
        
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Set the layout for the widget.
        self.setLayout(layout)