from typing import Literal, Dict
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QGroupBox,
)

from PyQt5.QtCore import pyqtSlot

class StatusItem(QWidget):
    def __init__(self, name):
        super().__init__()
        self.name = name

        layout = QHBoxLayout()

        self.name_label = QLabel(self.name + ":")
        self.name_label.setStyleSheet("font-weight: bold;")
        self.status_label = QLabel("Inactive")
        self.status_label.setStyleSheet("color: red;")  # Default color for "Inactive"

        layout.addWidget(self.name_label)
        layout.addWidget(self.status_label)

        self.current_status = "Inactive"  # Track the current status
        
        self.setLayout(layout)

    def set_status(self, status: Literal["Inactive", "Active"]):
        if status == self.current_status:
            return  # No update needed if status is unchanged
        self.current_status = status  # Update the current status
        if status == "Active":
            self.status_label.setText(status)
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        elif status == "Inactive":
            self.status_label.setText(status)
            self.status_label.setStyleSheet("color: red; font-weight: bold;")


class StatusBar(QWidget):

    STATUS_NAME_LIST = [
        # "AMR Base",
        "IMU",
        "Left GPS",
        "Right GPS",
        "Heading",
        "RTCM",
        "Lidar",
    ]

    def __init__(self):
        super().__init__()
        
        layout = QHBoxLayout()
        group_box = QGroupBox("Status")
        # set the size of text in the group box
        group_box.setStyleSheet("QGroupBox { font-size: 16px; font-weight: bold; }")
        
        status_layout = QHBoxLayout()
        
        self.status_item_dict = {}

        for status_name in self.STATUS_NAME_LIST:
            status_item = StatusItem(status_name)
            status_layout.addWidget(status_item)
            status_layout.addSpacing(20)
            self.status_item_dict[status_name] = status_item

        status_layout.addStretch(1)
        
        group_box.setLayout(status_layout)
        layout.addWidget(group_box)
        
        self.setLayout(layout)
        self.setFixedHeight(100)
        
    def update_status(self, name: str, status: Literal["Inactive", "Active"]):
        """
        Updates the status of the specific StatusItem identified by `name`.

        :param name: The name of the status item to update.
        :param status: The new status, either "Inactive" or "Active".
        """
        if name in self.status_item_dict:
            self.status_item_dict[name].set_status(status)
        else:
            # raise KeyError(f"Status item with name '{name}' not found.")
            pass
    
    def reset_status(self):
        """
        Resets the status of all StatusItems to "Inactive".
        """
        for status_item in self.status_item_dict.values():
            status_item.set_status("Inactive")
    
    @pyqtSlot(dict)
    def on_status_signal_received(self, status_dict: Dict[str, str]):
        
        for name, status in status_dict.items():
            self.update_status(name, status)

        
