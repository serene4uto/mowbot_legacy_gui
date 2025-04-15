from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
)

from PyQt5.QtCore import (
    pyqtSignal,
    pyqtSlot,
)

from .status_bar_view import StatusBarView
from .menu_box_view import MenuBoxView
from .multi_panel_view import MultiPanelView
class MainView(QWidget):
    
    signal_settings_btn_clicked = pyqtSignal()
    signal_logger_btn_clicked = pyqtSignal()
    signal_navigator_btn_clicked = pyqtSignal()
    
    signal_bringup_btn_clicked = pyqtSignal(str)
    signal_localize_btn_clicked = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self._config = config
        
        self._is_bringup = False
        self._is_localizing = False
        self._is_navigating = False
        
        self.status_bar = StatusBarView()
        self.menu_box = MenuBoxView()
        self.multi_panel = MultiPanelView(config=self._config)
        
        self.bringup_btn = QPushButton("Start Bringup")
        self.bringup_btn.setFixedHeight(80)
        self.bringup_btn.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: green")
        self.bringup_btn.setEnabled(True)
        
        self.localize_btn = QPushButton("Start Localize")
        self.localize_btn.setFixedHeight(80)
        self.localize_btn.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: green")
        self.localize_btn.setEnabled(True)
        
        self._init_ui()
        self._connect_button_events()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.status_bar)
        layout.addSpacing(10)
        
        hlayout = QHBoxLayout()
        
        hleft_layout = QVBoxLayout()
        hleft_layout.addWidget(self.menu_box)
        hleft_layout.stretch(1)
        hleft_layout.addSpacing(10)
        hleft_layout.addWidget(self.bringup_btn)
        hleft_layout.addSpacing(10)
        hleft_layout.addWidget(self.localize_btn)
        hlayout.addLayout(hleft_layout)
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
        
    def on_bringup_btn_clicked(self):
        """Handle the bringup button click event."""
        if not self._is_bringup:
            # Begin bringup process
            self.bringup_btn.setEnabled(False)
            self.bringup_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: gray")
            self.bringup_btn.setText("...")
            self.signal_bringup_btn_clicked.emit("start")
        else:
            # End bringup process
            self.bringup_btn.setEnabled(False)
            self.bringup_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: gray")
            self.bringup_btn.setText("...")
            self.signal_bringup_btn_clicked.emit("stop")
    
    def on_localize_btn_clicked(self):
        """Handle the localize button click event."""
        if not self._is_localizing:
            # Begin localization process
            self.localize_btn.setEnabled(False)
            self.localize_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: gray")
            self.localize_btn.setText("...")
            self.signal_localize_btn_clicked.emit("start")
        else:
            # End localization process
            self.localize_btn.setEnabled(False)
            self.localize_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: gray")
            self.localize_btn.setText("...")
            self.signal_localize_btn_clicked.emit("stop")
            
    def on_navigate_btn_clicked(self):
        """Handle the navigate button click event."""
        if not self._is_navigating:
            # Begin navigation process
            self.multi_panel.waypoints_navigator_panel.start_nav_wpfl_btn.setEnabled(False)
            self.multi_panel.waypoints_navigator_panel.start_nav_wpfl_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: gray")
            self.multi_panel.waypoints_navigator_panel.start_nav_wpfl_btn.setText("...")
            self.signal_navigate_btn_clicked.emit("start")
        else:
            # End navigation process
            self.multi_panel.waypoints_navigator_panel.start_nav_wpfl_btn.setEnabled(False)
            self.multi_panel.waypoints_navigator_panel.start_nav_wpfl_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: gray")
            self.multi_panel.waypoints_navigator_panel.start_nav_wpfl_btn.setText("...")
            self.signal_navigate_btn_clicked.emit("stop")
        
        
    @pyqtSlot(str)
    def on_signal_bringup_progress_status(self, status: str):
        """
        Update the bringup button based on the status.
        
        :param status: The status of the bringup process.
        """
        if status == "started":
            self._is_bringup = True
            self.bringup_btn.setText("Stop Bringup")
            self.bringup_btn.setEnabled(True)
            self.bringup_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: red")
        elif status == "stopped":
            self._is_bringup = False
            self.bringup_btn.setText("Start Bringup")
            self.bringup_btn.setEnabled(True)
            self.bringup_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: green")
    
    @pyqtSlot(str)
    def on_signal_localize_progress_status(self, status: str):
        """
        Update the localize button based on the status.
        
        :param status: The status of the localization process.
        """
        if status == "started":
            self._is_localizing = True
            self.localize_btn.setText("Stop Localize")
            self.localize_btn.setEnabled(True)
            self.localize_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: red")
        elif status == "stopped":
            self._is_localizing = False
            self.localize_btn.setText("Start Localize")
            self.localize_btn.setEnabled(True)
            self.localize_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: green")
            
    @pyqtSlot(str)
    def on_signal_navigate_progress_status(self, status: str):
        """
        Update the navigate button based on the status.
        
        :param status: The status of the navigation process.
        """
        if status == "started":
            self._is_navigating = True
            self.multi_panel.waypoints_navigator_panel.start_nav_wpfl_btn.setText("Stop")
            self.multi_panel.waypoints_navigator_panel.start_nav_wpfl_btn.setEnabled(True)
            self.multi_panel.waypoints_navigator_panel.start_nav_wpfl_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: red")
        elif status == "stopped":
            self._is_navigating = False
            self.multi_panel.waypoints_navigator_panel.start_nav_wpfl_btn.setText("Start")
            self.multi_panel.waypoints_navigator_panel.start_nav_wpfl_btn.setEnabled(True)
            self.multi_panel.waypoints_navigator_panel.start_nav_wpfl_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: green")
