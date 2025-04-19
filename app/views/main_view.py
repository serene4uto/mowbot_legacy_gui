from typing import Dict
import pathlib
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QLabel,
)

from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    pyqtSlot,
)

from PyQt5.QtGui import QFont, QIcon

from .status_bar_view import StatusBarView
from .menu_box_view import MenuBoxView
from .multi_panel_view import MultiPanelView

from app.utils.logger import logger
class MainView(QWidget):
    
    signal_settings_btn_clicked = pyqtSignal()
    signal_logger_btn_clicked = pyqtSignal()
    signal_navigator_btn_clicked = pyqtSignal()
    
    signal_bringup_btn_clicked = pyqtSignal(str) # start or stop
    signal_localization_btn_clicked = pyqtSignal(str) # start or stop
    signal_navigation_wp_follow_btn_clicked = pyqtSignal(str) # start or stop
    
    signal_log_btn_clicked = pyqtSignal()
    signal_log_remove_btn_clicked = pyqtSignal()
    signal_log_clear_btn_clicked = pyqtSignal()
    signal_log_save_btn_clicked = pyqtSignal(str, dict) # save_path, data
    
    signal_nav_wpfl_waypoints_load_btn_clicked = pyqtSignal(str) # load_file_path
    signal_nav_wpfl_params_load_btn_clicked = pyqtSignal(str) # load_file_path
    
    signal_exit_btn_clicked = pyqtSignal()
    signal_shutdown_btn_clicked = pyqtSignal()
    signal_restart_btn_clicked = pyqtSignal()
    
    signal_settings_load_btn_clicked = pyqtSignal(str)  # str: file path
    signal_settings_save_btn_clicked = pyqtSignal(str, dict)  # str: file path, dict: yaml data
    
    def __init__(self, config):
        super().__init__()
        self._config = config
        
        self._is_bringup = False
        self._is_localizing = False
        self._is_navigating = False
        
        self._is_waiting_for_bringup = None
        self._is_waiting_for_localization = None
        self._is_waiting_for_navigation = None
        
        self.title_label = QLabel("MOWBOT CONTROL SYSTEM")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #2c3e50;
            background-color: #27ae60; 
        """)
        
        self.status_bar = StatusBarView()
        self.menu_box = MenuBoxView()
        self.multi_panel = MultiPanelView(config=self._config)
        
        self.bringup_btn = QPushButton("Start Bringup")
        self.bringup_btn.setFixedHeight(80)
        self.bringup_btn.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: green")
        self.bringup_btn.setEnabled(True)
        
        self.localize_btn = QPushButton("Start Localization")
        self.localize_btn.setFixedHeight(80)
        self.localize_btn.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: green")
        self.localize_btn.setEnabled(True)
        
        # Restart button
        self.restart_btn = QPushButton()
        self.restart_btn.setFixedWidth(80)
        self.restart_btn.setFixedHeight(80)
        self.restart_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1c40f;
                border-radius: 25px;
                border: none;
            }
            QPushButton:hover {
                background-color: #d4ac0d;
            }
            QPushButton:pressed {
                background-color: #b7950b;
            }
            QPushButton:disabled {
                background-color: #aaaaaa;
            }
        """)
        self.restart_btn.setIcon(QIcon(
            str(pathlib.Path(__file__).parent.parent / "resources" / "icons" / "restart.png")))
        self.restart_btn.setIconSize(self.restart_btn.size() * 0.6)
        self.restart_btn.setToolTip("Restart System")
        
        self.shutdown_btn = QPushButton()
        self.shutdown_btn.setFixedWidth(80)
        self.shutdown_btn.setFixedHeight(80)
        self.shutdown_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                border-radius: 25px;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a33022;
            }
            QPushButton:disabled {
                background-color: #aaaaaa;
            }
        """)
        self.shutdown_btn.setIcon(QIcon(
            str(pathlib.Path(__file__).parent.parent / "resources" / "icons" / "shutdown.png")))
        self.shutdown_btn.setIconSize(self.shutdown_btn.size() * 0.6)  # Adjust size as needed
        self.shutdown_btn.setToolTip("Shutdown System")
        
        self.exit_btn = QPushButton()
        self.exit_btn.setFixedWidth(80)
        self.exit_btn.setFixedHeight(80)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                border-radius: 25px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
            QPushButton:disabled {
                background-color: #aaaaaa;
            }
        """)
        self.exit_btn.setIcon(QIcon(
            str(pathlib.Path(__file__).parent.parent / "resources" / "icons" / "exit.png")))
        self.exit_btn.setIconSize(self.exit_btn.size() * 0.6)
        self.exit_btn.setToolTip("Exit Application")
        
        self.menu_box.task_menu_grb.setEnabled(False)
        self.multi_panel.waypoints_logger_panel.setEnabled(False)
        self.multi_panel.waypoints_navigator_panel.setEnabled(False)
        self.status_bar.setEnabled(False)
        self.localize_btn.setEnabled(False)
        self.localize_btn.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: gray")
        
        # alias for signal connections
        self.signal_settings_load_btn_clicked = \
            self.multi_panel.settings_panel.signal_load_btn_clicked
        self.signal_settings_save_btn_clicked = \
            self.multi_panel.settings_panel.signal_save_btn_clicked
        
        self._init_ui()
        self._connect_button_events()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addSpacing(10)
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.status_bar)
        top_layout.addSpacing(10)
        top_layout.addStretch(1)
        top_layout.addWidget(self.shutdown_btn)
        top_layout.addSpacing(10)
        top_layout.addWidget(self.restart_btn)
        top_layout.addSpacing(10)
        top_layout.addWidget(self.exit_btn)
        layout.addLayout(top_layout)
        layout.addSpacing(10)
        
        hlayout = QHBoxLayout()
        
        hleft_layout = QVBoxLayout()
        hleft_layout.addWidget(self.menu_box)
        hleft_layout.stretch(1)
        hleft_layout.addSpacing(10)
        hleft_layout.addWidget(self.localize_btn)
        hleft_layout.addSpacing(10)
        hleft_layout.addWidget(self.bringup_btn)
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
        self.bringup_btn.clicked.connect(self.on_bringup_btn_clicked)
        self.localize_btn.clicked.connect(self.on_localize_btn_clicked)
        self.multi_panel.waypoints_navigator_panel.option_bar.start_nav_wpfl_btn.clicked.connect(
            self.on_navigate_btn_clicked)
        self.multi_panel.waypoints_logger_panel.option_bar.log_btn.clicked.connect(
            self.on_waypoint_log_btn_clicked)
        self.multi_panel.waypoints_logger_panel.option_bar.rm_btn.clicked.connect(
            self.on_selected_logged_waypoint_remove_btn_clicked)
        self.multi_panel.waypoints_logger_panel.option_bar.clear_btn.clicked.connect(
            self.on_logged_waypoints_clear_btn_clicked)
        self.multi_panel.waypoints_logger_panel.option_bar.save_btn.clicked.connect(
            self.on_logged_waypoints_save_btn_clicked)
        
        self.multi_panel.waypoints_navigator_panel.option_bar.load_wp_btn.clicked.connect(
            self.on_nav_wpfl_waypoints_load_btn_clicked)
        self.multi_panel.waypoints_navigator_panel.option_bar.load_params_btn.clicked.connect(
            self.on_nav_wpfl_params_load_btn_clicked)
        
        self.exit_btn.clicked.connect(self.on_exit_btn_clicked)
        self.shutdown_btn.clicked.connect(self.on_shutdown_btn_clicked)
        self.restart_btn.clicked.connect(self.on_restart_btn_clicked)
        
        self.multi_panel.settings_panel.params_load_btn.clicked.connect(
            self.on_settings_load_btn_clicked)
        self.multi_panel.settings_panel.params_save_btn.clicked.connect(
            self.on_settings_save_btn_clicked)
        self.multi_panel.settings_panel.params_sync_btn.clicked.connect(
            self.on_settings_sync_btn_clicked)
        
    def on_exit_btn_clicked(self):
        """Forward the exit button event."""
        # self.signal_exit_btn_clicked.emit()
        self.signal_exit_btn_clicked.emit()
        
    def on_shutdown_btn_clicked(self):
        """Forward the shutdown button event."""
        # self.signal_shutdown_btn_clicked.emit()
        self.signal_shutdown_btn_clicked.emit()
        
    def on_restart_btn_clicked(self):
        """Forward the restart button event."""
        # self.signal_restart_btn_clicked.emit()
        self.signal_restart_btn_clicked.emit()
        
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
        
        # if self._is_waiting_for_bringup is not None:
        #     return
        
        if not self._is_bringup:
            # Begin bringup process
            self.bringup_btn.setEnabled(False)
            self.bringup_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: gray")
            self.bringup_btn.setText("...")
            self.signal_bringup_btn_clicked.emit("start")
            self._is_waiting_for_bringup = "start"
        else:
            # End bringup process
            self.bringup_btn.setEnabled(False)
            self.bringup_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: gray")
            self.bringup_btn.setText("...")
            self.signal_bringup_btn_clicked.emit("stop")
            self._is_waiting_for_bringup = "stop"
            # stop localization and navigation if they are running
            if self._is_localizing:
                self.on_localize_btn_clicked()
            if self._is_navigating:
                self.on_navigate_btn_clicked()
    
    def on_localize_btn_clicked(self):
        """Handle the localize button click event."""
        
        # if self._is_waiting_for_localization is not None:
        #     return
        
        logger.info(f"localize_btn clicked: {self._is_waiting_for_localization}")
        if not self._is_localizing:
            # Begin localization process
            self.localize_btn.setEnabled(False)
            self.localize_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: gray")
            self.localize_btn.setText("...")
            self.signal_localization_btn_clicked.emit("start")
            self._is_waiting_for_localization = "start"
        else:
            # End localization process
            self.localize_btn.setEnabled(False)
            self.localize_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: gray")
            self.localize_btn.setText("...")
            self.signal_localization_btn_clicked.emit("stop")
            self._is_waiting_for_localization = "stop"
            
    def on_navigate_btn_clicked(self):
        """Handle the navigate button click event."""
        
        # if self._is_waiting_for_navigation is not None:
        #     return
        
        if not self._is_navigating:
            # Begin navigation process
            self.multi_panel.waypoints_navigator_panel.option_bar.start_nav_wpfl_btn.setEnabled(False)
            self.multi_panel.waypoints_navigator_panel.option_bar.start_nav_wpfl_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: gray")
            self.multi_panel.waypoints_navigator_panel.option_bar.start_nav_wpfl_btn.setText("...")
            self.signal_navigation_wp_follow_btn_clicked.emit("start")
            self._is_waiting_for_navigation = "start"
        else:
            # End navigation process
            self.multi_panel.waypoints_navigator_panel.option_bar.start_nav_wpfl_btn.setEnabled(False)
            self.multi_panel.waypoints_navigator_panel.option_bar.start_nav_wpfl_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: gray")
            self.multi_panel.waypoints_navigator_panel.option_bar.start_nav_wpfl_btn.setText("...")
            self.signal_navigation_wp_follow_btn_clicked.emit("stop")
            self._is_waiting_for_navigation = "stop"
            
    def on_waypoint_log_btn_clicked(self):
        """Forward the log button event."""
        self.multi_panel.waypoints_logger_panel.update_table_map_with_logged_waypoint(
            latitude=self.multi_panel.waypoints_logger_panel.get_last_gps_lat(),
            longitude=self.multi_panel.waypoints_logger_panel.get_last_gps_lon(),
            heading=self.multi_panel.waypoints_logger_panel.get_last_heading()
        )
        self.signal_log_btn_clicked.emit()
        
    def on_selected_logged_waypoint_remove_btn_clicked(self):
        """Forward the remove button event."""
        self.multi_panel.waypoints_logger_panel.remove_selected_log_waypoints()
        self.signal_log_remove_btn_clicked.emit()
        
    def on_logged_waypoints_clear_btn_clicked(self):
        """Forward the clear button event."""
        self.multi_panel.waypoints_logger_panel.clear_log_waypoints()
        self.signal_log_clear_btn_clicked.emit()
        
    def on_logged_waypoints_save_btn_clicked(self):
        """Forward the save button event."""
        save_path = self.multi_panel.waypoints_logger_panel.prompt_for_save_file()
        current_waypoints = self.multi_panel.waypoints_logger_panel.get_current_logged_waypoints()
        if not save_path:
            return
        if not current_waypoints:
            return
        self.signal_log_save_btn_clicked.emit(
            save_path,
            {"waypoints": current_waypoints}
        )
        # logger.info(f"Save path: {save_path}")
        
    def on_nav_wpfl_waypoints_load_btn_clicked(self):
        """Forward the waypoint load button event."""
        load_file_path = self.multi_panel.waypoints_navigator_panel.prompt_for_waypoint_file_load()
        if not load_file_path:
            return
        self.signal_nav_wpfl_waypoints_load_btn_clicked.emit(load_file_path)
    
    def on_nav_wpfl_params_load_btn_clicked(self):
        """Forward the waypoint params load button event."""
        load_file_path = self.multi_panel.waypoints_navigator_panel.prompt_for_params_file_load()
        if not load_file_path:
            return
        self.signal_nav_wpfl_params_load_btn_clicked.emit(load_file_path)
        
        
    def on_settings_load_btn_clicked(self):
        """Forward the settings load button event."""
        load_file_path = self.multi_panel.settings_panel.prompt_file_dialog_for_load()
        if not load_file_path:
            return
        self.signal_settings_load_btn_clicked.emit(load_file_path)
        
    def on_settings_save_btn_clicked(self):
        """Forward the settings save button event."""
        save_file_path = self.multi_panel.settings_panel.prompt_file_dialog_for_save()
        yaml_data = self.multi_panel.settings_panel.get_params()
        if not save_file_path:
            return
        if not yaml_data:
            logger.warning("No data to save.")
            return
        self.signal_settings_save_btn_clicked.emit(
            save_file_path, 
            yaml_data
        )
        
    def on_settings_sync_btn_clicked(self):
        """Forward the settings sync button event."""
        self.signal_settings_load_btn_clicked.emit(
            self.multi_panel.settings_panel.sync_params_file_path
        )
        
    @pyqtSlot(str)
    def on_signal_bringup_container_status(self, status: str):
        """
        Update the bringup button based on the status.
        
        :param status: The status of the bringup container.
        """
        
        if self._is_waiting_for_bringup is None:
            return
        
        if status == "started" and self._is_waiting_for_bringup == "start":
            self._is_bringup = True
            self.bringup_btn.setText("Stop Bringup")
            self.bringup_btn.setEnabled(True)
            self.bringup_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: red")
            
            # Enable
            self.localize_btn.setEnabled(True)
            self.localize_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: green")
            self.localize_btn.setText("Start Localization")
            self.menu_box.task_menu_grb.setEnabled(True)
            self.multi_panel.waypoints_logger_panel.setEnabled(True)
            self.multi_panel.waypoints_navigator_panel.setEnabled(True)
            self.status_bar.setEnabled(True)
            self._is_waiting_for_bringup = None
            
        elif status == "stopped" and self._is_waiting_for_bringup == "stop":
            self._is_bringup = False
            self.bringup_btn.setText("Start Bringup")
            self.bringup_btn.setEnabled(True)
            self.bringup_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: green")
            
            # Reset and disable
            self.localize_btn.setEnabled(False)
            self.localize_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: gray")
            self.localize_btn.setText("Start Localization")
            self.menu_box.task_menu_grb.setEnabled(False)
            self.multi_panel.waypoints_logger_panel.setEnabled(False)
            self.multi_panel.waypoints_navigator_panel.setEnabled(False)
            self.status_bar.setEnabled(False)
            self._is_waiting_for_bringup = None


    @pyqtSlot(str)
    def on_signal_localization_container_status(self, status: str):
        """
        Update the localize button based on the status.
        
        :param status: The status of the localization container.
        """
        if self._is_waiting_for_localization is None:
            return
        if status == "started" and self._is_waiting_for_localization == "start":
            self._is_localizing = True
            self.localize_btn.setText("Stop Localization")
            self.localize_btn.setEnabled(True)
            self.localize_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: red")
            self._is_waiting_for_localization = None
            
        elif status == "stopped" and self._is_waiting_for_localization == "stop":
            self._is_localizing = False
            self.localize_btn.setText("Start Localization")
            if self._is_bringup: 
                self.localize_btn.setEnabled(True)
                self.localize_btn.setStyleSheet(
                    "font-size: 16px; font-weight: bold; color: green")
            self._is_waiting_for_localization = None

    @pyqtSlot(str)
    def on_signal_navigation_container_status(self, status: str):
        """
        Update the navigate button based on the status.
        
        :param status: The status of the navigation container.
        """
        if self._is_waiting_for_navigation is None:
            return
        
        if status == "started" and self._is_waiting_for_navigation == "start":
            self._is_navigating = True
            self.multi_panel.waypoints_navigator_panel.option_bar.start_nav_wpfl_btn.setText("Stop")
            self.multi_panel.waypoints_navigator_panel.option_bar.start_nav_wpfl_btn.setEnabled(True)
            self.multi_panel.waypoints_navigator_panel.option_bar.start_nav_wpfl_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: red")
            self._is_waiting_for_navigation = None
            
        elif status == "stopped" and self._is_waiting_for_navigation == "stop":
            self._is_navigating = False
            self.multi_panel.waypoints_navigator_panel.option_bar.start_nav_wpfl_btn.setText("Start")
            self.multi_panel.waypoints_navigator_panel.option_bar.start_nav_wpfl_btn.setEnabled(True)
            self.multi_panel.waypoints_navigator_panel.option_bar.start_nav_wpfl_btn.setStyleSheet(
                "font-size: 16px; font-weight: bold; cooption_bar.lor: green")
            self._is_waiting_for_navigation = None
            
            
    @pyqtSlot(dict)
    def on_signal_update_health_status(self, status_dict: Dict[str, str]):
        """
        Update the health status of a specific item.
        """
        logger.debug(f"Health status updated: {status_dict}")
        for name, status in status_dict.items():
            self.status_bar.update_status(name, status)
            
            
    @pyqtSlot(dict)
    def on_signal_gps_fix_received(self, data: dict):
        # logger.info(f" GPS Fix signal received: {data}")
        self.multi_panel.waypoints_logger_panel.update_gps_info(
            latitude=data['latitude'],
            longitude=data['longitude'],
        )
        self.multi_panel.waypoints_navigator_panel.update_gps_info(
            latitude=data['latitude'],
            longitude=data['longitude'],
        )
        
        
    @pyqtSlot(dict)
    def on_signal_heading_quat_received(self, data: dict):
        # logger.info(f" Heading signal received: {data}")
        self.multi_panel.waypoints_logger_panel.update_heading_info(
            data=data,
        )
        self.multi_panel.waypoints_navigator_panel.update_heading_info(
            data=data,
        )
        
    @pyqtSlot(str, dict)
    def on_signal_waypoints_loaded(self, file_path: str, waypoints: dict):
        """
        Slot method to handle the waypoints loaded signal.
        """
        # Update the waypoint info display with the loaded waypoints
        self.multi_panel.waypoints_navigator_panel.update_load_waypoints_file_info(
            file_path=file_path)
        # update waypoint to map
        self.multi_panel.waypoints_navigator_panel.map_view.reset()
        for waypoint in waypoints["waypoints"]:
            self.multi_panel.waypoints_navigator_panel.map_view.add_gps_position_mark(
                latitude=waypoint["latitude"],
                longitude=waypoint["longitude"],
            )

    
    @pyqtSlot(str, dict)
    def on_signal_params_loaded(self, file_path: str, params: dict):
        """
        Slot method to handle the parameters loaded signal.
        """
        # Update the parameter info display with the loaded parameters
        self.multi_panel.waypoints_navigator_panel.update_load_params_file_info(
            file_path=file_path)
        
        
    @pyqtSlot(str, dict)
    def on_signal_settings_param_loaded(self, file_path: str, params: dict):
        """
        Slot method to handle the settings parameters loaded signal.
        """
        # Update the parameter info display with the loaded parameters
        self.multi_panel.settings_panel.update_load_params(
            yaml_data=params,
        )
        
