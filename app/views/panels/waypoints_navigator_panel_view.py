# waypoints_navigator_panel_view.py
import os
import numpy as np
from scipy.spatial.transform import Rotation as R
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
        
        self._last_gps_lat = None
        self._last_gps_lon = None
        self._last_gps_heading = None
        
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
        
        
    def prompt_for_waypoint_file_load(self):
        """
        Prompts the user to select a waypoint file for loading.
        """
        
        load_file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Waypoints File",
            self._config['mowbot_legacy_data_path'] + '/waypoints',
            "YAML Files (*.yaml);;All Files (*)",
        )
        
        return load_file_path
    
    def prompt_for_params_file_load(self):
        """
        Prompts the user to select a parameters file for loading.
        """
        
        load_file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Parameters File",
            self._config['mowbot_legacy_data_path'] + '/params',
            "YAML Files (*.yaml);;All Files (*)",
        )
        
        return load_file_path
    
    def update_gps_info(self, latitude: float, longitude: float):
        """
        Updates the map view's GPS marker and refreshes the GPS information display.
        """
        self._last_gps_lat = latitude
        self._last_gps_lon = longitude
        self.map_view.update_gps_position(latitude=latitude, longitude=longitude)
        self.gps_info_display.setText(
            f"lat: {latitude:.6f}, lon: {longitude:.6f}"
        )
        
    def update_heading_info(self, data: dict):
        """
        Converts quaternion heading data to a readable value, updates the map view's heading,
        and refreshes the heading information display.
        """
        quat = [data['x'], data['y'], data['z'], data['w']]
        euler = R.from_quat(quat).as_euler('xyz', degrees=True)
        yaw_enu = euler[2]
        yaw_ned = (90 - yaw_enu) % 360
        self.map_view.update_heading(heading=yaw_ned)
        self._last_heading = np.deg2rad(yaw_enu)
        self.hdg_info_display.setText(
            f"heading: {self._last_heading:.4f} rad"
        )
        
    def update_load_waypoints_file_info(self, file_path):
        """
        Updates the waypoints file information display.
        """
        self.option_bar.wp_info_display.setText(f"Waypoints: {file_path}")

    def update_load_params_file_info(self, file_path):
        """
        Updates the parameters file information display.
        """
        self.option_bar.param_info_display.setText(f"Params: {file_path}")
        
    
