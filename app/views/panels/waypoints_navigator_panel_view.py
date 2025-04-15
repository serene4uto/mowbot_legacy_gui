# waypoints_navigator_panel_view.py
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QGroupBox,
    QFileDialog,
)
from PyQt5.QtCore import pyqtSlot

from .map_view import MapView
from app.utils.logger import logger


class WaypointsNavigatorOptionBarView(QWidget):
    """
    A view component for the option bar in the waypoint navigation panel.
    """

    def __init__(
        self, 
        config
    ):
        super().__init__()
        self._config = config
        
        self.start_nav_wpfl_btn = QPushButton()
        self.start_nav_wpfl_btn.setText('Start')
        self.start_nav_wpfl_btn.setFixedSize(80, 80)
        self.start_nav_wpfl_btn.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: green")
        
        self.load_wp_btn = QPushButton("Load\r\nWaypoints")
        self.load_wp_btn.setFixedSize(150, 80)
        self.load_wp_btn.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: Black")
        
        self.load_params_btn = QPushButton("Load\r\nParams")
        self.load_params_btn.setFixedSize(100, 80)
        self.load_params_btn.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: Black")
        
        self.wp_info_display = QLabel()
        self.wp_info_display.setText("Waypoints: Empty")
        # self.wp_info_display.setFixedHeight(40)
        
        self.param_info_display = QLabel()
        self.param_info_display.setText("Params: Empty")
        # self.param_info_display.setFixedHeight(40)

        # Initialize UI
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout()
        bar_layout = QHBoxLayout()
        bar_layout.addWidget(self.start_nav_wpfl_btn)
        bar_layout.setSpacing(10)
        bar_layout.addWidget(self.load_wp_btn)
        bar_layout.setSpacing(10)
        bar_layout.addWidget(self.load_params_btn)
        bar_layout.setSpacing(10)
        # add info display
        info_grpbox = QGroupBox()
        info_layout = QVBoxLayout()
        info_layout.addWidget(self.wp_info_display)
        info_layout.setSpacing(10)
        info_layout.addWidget(self.param_info_display)
        info_layout.setSpacing(10)
        info_layout.addStretch(1)
        info_grpbox.setLayout(info_layout)
        bar_layout.addWidget(info_grpbox)
        bar_layout.setSpacing(10)
        # bar_layout.addStretch(1)
        layout.addLayout(bar_layout)
        layout.addStretch(1)
        self.setLayout(layout)
        
        
        
class WaypointsNavigatorPanelView(QWidget):
    """
    A view component for the waypoints navigator panel.
    """

    def __init__(
        self, 
        config
    ):
        super().__init__()
        self._config = config
        
        # Create subcomponents.
        self.option_bar = WaypointsNavigatorOptionBarView(
            config=self._config
        )
        self.map_view = MapView(
            config=self._config
        )

        self.gps_info_display = QLabel()
        self.hdg_info_display = QLabel()
        
        # Initialize UI
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.option_bar)
        layout.addSpacing(10)
        layout.addWidget(self.map_view)
        layout.addSpacing(10)

        # add info display
        info_layout = QHBoxLayout()
        info_layout.addWidget(self.gps_info_display)
        info_layout.setSpacing(10)
        info_layout.addWidget(self.hdg_info_display)
        info_layout.setSpacing(10)
        info_layout.addStretch(1)
        layout.addLayout(info_layout)
        
        layout.addStretch(1)
        self.setLayout(layout)