from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)

from PyQt5.QtCore import pyqtSignal

from .status_bar_view import StatusBarView
from .menu_box_view import MenuBoxView
from .multi_panel_view import MultiPanelView
class MainView(QWidget):
    signal_settings_btn_clicked = pyqtSignal()
    signal_logger_btn_clicked = pyqtSignal()
    signal_navigator_btn_clicked = pyqtSignal()

    def __init__(self, config):
        super().__init__()
        self._config = config
        
        self.status_bar = StatusBarView()
        self.menu_box = MenuBoxView()
        self.multi_panel = MultiPanelView(config=self._config)
        
        self._init_ui()
        self._connect_button_events()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.status_bar)
        layout.addSpacing(10)
        
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.menu_box)
        hlayout.addSpacing(10)
        hlayout.addWidget(self.multi_panel)
        layout.addLayout(hlayout)
        layout.addStretch(1)
        self.setLayout(layout)
    
    def _connect_button_events(self):
        """Connect button click events to their handlers."""
        self.menu_box.settings_btn.clicked.connect(self.on_settings_btn_clicked)
        self.menu_box.logger_btn.clicked.connect(self.on_logger_btn_clicked)
        self.menu_box.navigator_btn.clicked.connect(self.on_navigator_btn_clicked)
    
    def on_settings_btn_clicked(self):
        """Forward the settings button event from the menu and update the UI."""
        self.menu_box.highlight_button("settings")
        self.multi_panel.show_settings_panel()  # Assuming the method name reflects your panel's API.
        self.signal_settings_btn_clicked.emit()
        
    def on_logger_btn_clicked(self):
        """Forward the logger button event."""
        self.menu_box.highlight_button("logger")
        self.multi_panel.show_waypoints_logger_panel()
        self.signal_logger_btn_clicked.emit()
        
    def on_navigator_btn_clicked(self):
        """Forward the navigator button event."""
        self.menu_box.highlight_button("navigator")
        self.multi_panel.show_waypoints_navigator_panel()
        self.signal_navigator_btn_clicked.emit()
