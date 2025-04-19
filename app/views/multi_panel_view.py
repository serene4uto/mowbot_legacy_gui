# multipanel_view.py
from PyQt5.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QGroupBox, 
    QStackedWidget
)
from .panels import (
    SettingsPanelView,
    WaypointsLoggerPanelView,
    WaypointsNavigatorPanelView
)

class MultiPanelView(QWidget):
    def __init__(self, config):
        super().__init__()
        self._config = config

        self.stacked_widget = QStackedWidget()
        
        self.waypoints_logger_panel = WaypointsLoggerPanelView( 
            config=self._config
        )      
        self.waypoints_navigator_panel = WaypointsNavigatorPanelView(
            config=self._config
        )  
        self.settings_panel = SettingsPanelView(
            config=self._config
        )                                

        # Add panels to the stacked widget.
        self.stacked_widget.addWidget(self.waypoints_logger_panel)
        self.stacked_widget.addWidget(self.waypoints_navigator_panel)
        self.stacked_widget.addWidget(self.settings_panel)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        group_box = QGroupBox()  # Optional container for additional styling.
        group_layout = QVBoxLayout()
        group_layout.addWidget(self.stacked_widget)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        self.setLayout(layout)

    # View API methods for switching panels
    def show_waypoints_logger_panel(self):
        """Switches to the Waypoints Logger panel (Index 0)."""
        self.stacked_widget.setCurrentIndex(0)

    def show_waypoints_navigator_panel(self):
        """Switches to the Waypoints Navigator panel (Index 1)."""
        self.stacked_widget.setCurrentIndex(1)

    def show_settings_panel(self):
        """Switches to the Settings panel (Index 2)."""
        self.stacked_widget.setCurrentIndex(2)

