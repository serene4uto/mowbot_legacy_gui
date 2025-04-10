
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)



class SettingsDisplay(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        
        label = QLabel("Settings Display")
        
        layout.addWidget(label)
        self.setLayout(layout)