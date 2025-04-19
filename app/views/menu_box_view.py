# menu_box_view.py
from PyQt5.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QPushButton, 
    QGroupBox
)
from PyQt5.QtCore import pyqtSignal

class MenuBoxView(QWidget):
    
    def __init__(self):
        super().__init__()
        
        # Create buttons with new names
        self.settings_btn = QPushButton('Settings')
        self.settings_btn.setFixedHeight(50)
        
        self.logger_btn = QPushButton('Waypoint Logger')
        self.logger_btn.setFixedHeight(50)
        
        self.navigator_btn = QPushButton('Waypoint Navigator')
        self.navigator_btn.setFixedHeight(50)
        
        self.task_menu_grb = QGroupBox('Tasks')
        
        self._init_ui()
        
        # Optionally, highlight the default button (e.g., Waypoint Logger).
        self.highlight_button("logger")
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Create a group box for the menu
        menu_grb = QGroupBox('Menu')
        menu_grb.setStyleSheet("QGroupBox { font-size: 16px; font-weight: bold; }")
        menu_layout = QVBoxLayout()
        menu_layout.addWidget(self.settings_btn)
        
        # Create a nested group box for task-related buttons
        self.task_menu_grb.setStyleSheet("QGroupBox { font-size: 14px; font-weight: bold; }")
        task_menu_layout = QVBoxLayout()
        self.task_menu_grb.setLayout(task_menu_layout)
        task_menu_layout.addWidget(self.logger_btn)
        task_menu_layout.addSpacing(10)
        task_menu_layout.addWidget(self.navigator_btn)
        task_menu_layout.addSpacing(10)
        task_menu_layout.addStretch(1)
        
        menu_layout.addWidget(self.task_menu_grb)
        menu_grb.setLayout(menu_layout)
        layout.addWidget(menu_grb)
        
        self.setLayout(layout)
        self.setFixedWidth(250)
    
    def reset_btns(self):
        """Resets all buttons to default style and enables them."""
        self.settings_btn.setEnabled(True)
        self.logger_btn.setEnabled(True)
        self.navigator_btn.setEnabled(True)
        self.settings_btn.setStyleSheet("")
        self.logger_btn.setStyleSheet("")
        self.navigator_btn.setStyleSheet("")
    
    def highlight_button(self, button_name: str):
        """
        Highlights the specified button and resets all others.
        
        :param button_name: One of "settings", "logger", or "navigator".
        """
        self.reset_btns()
        style = "background-color: lightblue; font-size: 16px; font-weight: bold;"
        if button_name == "settings":
            self.settings_btn.setStyleSheet(style)
        elif button_name == "logger":
            self.logger_btn.setStyleSheet(style)
        elif button_name == "navigator":
            self.navigator_btn.setStyleSheet(style)
        
