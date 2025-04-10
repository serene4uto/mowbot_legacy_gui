from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
)



class WaypointsFollowDisplay(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        
        label = QLabel("Waypoint Follow Display")
        
        layout.addWidget(label)
        
        self.setLayout(layout)
        
        