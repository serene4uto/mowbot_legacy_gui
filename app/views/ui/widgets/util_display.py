from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
)




class UtilDisplay(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        
        label = QLabel("utilities")
        
        layout.addWidget(label)
        
        self.setLayout(layout)
        
        