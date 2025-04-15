from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QGroupBox,
)
from PyQt5.QtCore import pyqtSignal, pyqtSlot

class MenuBox(QWidget):
    
    settings_btn_clicked_signal = pyqtSignal()
    set_wp_task_btn_clicked_signal = pyqtSignal()
    follow_wp_task_btn_clicked_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.settings_btn = QPushButton('Settings')
        self.settings_btn.setFixedHeight(50)
        self.set_wp_task_btn = QPushButton('Set Waypoints')
        self.set_wp_task_btn.setFixedHeight(50)
        self.follow_wp_task_btn = QPushButton('Follow Waypoints')
        self.follow_wp_task_btn.setFixedHeight(50)
        
        self._init_ui()
        self._connect_signals()
        
        # first index
        self.set_wp_task_btn.setStyleSheet(
            "background-color: lightblue; font-size: 16px; font-weight: bold;"
        )
        
        
    def _init_ui(self):
        layout = QVBoxLayout()
        menu_grb = QGroupBox('Menu')
        menu_grb.setStyleSheet(
            "QGroupBox { font-size: 16px; font-weight: bold; }")
        menu_layout = QVBoxLayout()
        menu_layout.addWidget(self.settings_btn)
        
        task_menu_grb = QGroupBox('Tasks')
        task_menu_grb.setStyleSheet(
            "QGroupBox { font-size: 14px; font-weight: bold; }")
        task_menu_layout = QVBoxLayout()
        task_menu_grb.setLayout(task_menu_layout)
        task_menu_layout.addWidget(self.set_wp_task_btn)
        task_menu_layout.setSpacing(10)
        task_menu_layout.addWidget(self.follow_wp_task_btn)
        task_menu_layout.setSpacing(10)
        task_menu_layout.addStretch(1)
        menu_layout.addWidget(task_menu_grb)
        
        menu_grb.setLayout(menu_layout)
        layout.addWidget(menu_grb)

        self.setLayout(layout)
        
        
    def _connect_signals(self):
        self.settings_btn.clicked.connect(self.on_settings_btn_clicked)
        self.set_wp_task_btn.clicked.connect(self.on_set_wp_task_btn_clicked)
        self.follow_wp_task_btn.clicked.connect(self.on_follow_wp_task_btn_clicked)
        
        
    def reset_btns(self):
        self.settings_btn.setEnabled(True)
        self.set_wp_task_btn.setEnabled(True)
        self.follow_wp_task_btn.setEnabled(True)
        self.settings_btn.setStyleSheet("")
        self.set_wp_task_btn.setStyleSheet("")
        self.follow_wp_task_btn.setStyleSheet("")
        
     
    def on_settings_btn_clicked(self):
        self.settings_btn_clicked_signal.emit()
        self.reset_btns()
        self.settings_btn.setStyleSheet(
            "background-color: lightblue; font-size: 16px; font-weight: bold;"
        )
        

    def on_set_wp_task_btn_clicked(self):
        self.set_wp_task_btn_clicked_signal.emit()
        self.reset_btns()
        self.set_wp_task_btn.setStyleSheet(
            "background-color: lightblue; font-size: 16px; font-weight: bold;"
        )
        
        
    def on_follow_wp_task_btn_clicked(self):
        self.follow_wp_task_btn_clicked_signal.emit()
        self.reset_btns()
        self.follow_wp_task_btn.setStyleSheet(
            "background-color: lightblue; font-size: 16px; font-weight: bold;"
        )
        
        
    
