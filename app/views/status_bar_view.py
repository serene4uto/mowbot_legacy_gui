from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QGroupBox


class StatusItem(QWidget):
    def __init__(self, name: str):
        super().__init__()

        layout = QHBoxLayout()

        self.name_label = QLabel(f"{name}:")
        self.name_label.setStyleSheet("font-weight: bold;")

        self.status_label = QLabel("Inactive")
        self.status_label.setStyleSheet("color: red;")

        layout.addWidget(self.name_label)
        layout.addWidget(self.status_label)

        self.setLayout(layout)


class StatusBarView(QWidget):
    
    STATUS_NAME_LIST = [
        "IMU",
        "GPS",
        "Heading",
        "RTCM",
        "Lidar",
    ]

    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        group_box = QGroupBox("Status")
        group_box.setStyleSheet("QGroupBox { font-size: 16px; font-weight: bold; }")

        status_layout = QHBoxLayout()

        self.status_item_dict = {}

        for name in self.STATUS_NAME_LIST:
            item = StatusItem(name)
            status_layout.addWidget(item)
            status_layout.addSpacing(20)
            self.status_item_dict[name] = item

        status_layout.addStretch(1)
        group_box.setLayout(status_layout)
        layout.addWidget(group_box)

        self.setLayout(layout)
        self.setFixedHeight(100)
