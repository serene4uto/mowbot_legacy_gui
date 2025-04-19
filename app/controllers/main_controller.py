# main_controller.py
from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
    pyqtSlot,
    QTimer,
)
from PyQt5 import (
    QtWidgets
)


from app.views import MainView
from app.models import MainModel
from app.utils.logger import logger

class MainController(QObject):
    """
    MainController is responsible for managing the main view and its interactions with the model.
    """
    def __init__(
        self, 
        config: dict,
        app: QtWidgets.QApplication,
        main_view: MainView, 
        main_model: MainModel,
    ):
        """
        Initializes the MainController with the main view and model.
        
        Args:
            main_view (MainView): The main view of the application.
            main_model (MainModel): The main model of the application.
        """
        super().__init__()
        self._config = config
        self._app = app
        self._main_view = main_view
        self._main_model = main_model
        
        self._main_model.ros2_launch_container_model.start_periodic_tasks(
            status_interval_ms=1000,
            container_interval_ms=1000,
        )
        
        self._app.aboutToQuit.connect(self.on_app_exit)
        
        # Button click signals
        self._main_view.signal_bringup_btn_clicked.connect(
            self.on_signal_bringup_btn_clicked,
        )
        self._main_view.signal_localization_btn_clicked.connect(
            self.on_signal_localization_btn_clicked,
        )
        self._main_view.signal_navigation_wp_follow_btn_clicked.connect(
            self.on_signal_navigation_wp_follow_btn_clicked,
        )
        self._main_view.signal_log_save_btn_clicked.connect(
            self.on_signal_log_save_btn_clicked,
        )
        self._main_view.signal_nav_wpfl_waypoints_load_btn_clicked.connect(
            self.on_signal_load_waypoints_btn_clicked,
        )
        self._main_view.signal_nav_wpfl_params_load_btn_clicked.connect(
            self.on_signal_load_params_btn_clicked,
        )
        self._main_view.signal_exit_btn_clicked.connect(
            self.on_app_exit,
        )
        self._main_view.signal_shutdown_btn_clicked.connect(
            self.on_signal_shutdown_btn_clicked,
        )
        self._main_view.signal_restart_btn_clicked.connect(
            self.on_signal_restart_btn_clicked,
        )
        self._main_view.signal_settings_load_btn_clicked.connect(
            self.on_signal_settings_load_btn_clicked,
        )
        self._main_view.signal_settings_save_btn_clicked.connect(
            self.on_signal_settings_save_btn_clicked,
        )
        
        # Container status update signals
        self._main_model.ros2_launch_container_model.signal_container_status_updated.connect(
            self.on_signal_container_status_updated,
        )
        
        # Foxglove WebSocket signals
        self._main_model.foxglove_ws_model.signal_health_status.connect(
            self._main_view.on_signal_update_health_status,
        )
        self._main_model.foxglove_ws_model.signal_gps_fix.connect(
            self._main_view.on_signal_gps_fix_received,
        )
        self._main_model.foxglove_ws_model.signal_heading_quat.connect(
            self._main_view.on_signal_heading_quat_received,
        )
        
        # others
        self._main_model.signal_on_waypoints_loaded.connect(
            self._main_view.on_signal_waypoints_loaded,
        )
        self._main_model.signal_on_params_loaded.connect(
            self._main_view.on_signal_params_loaded,
        )
        self._main_model.signal_on_settings_param_loaded.connect(
            self._main_view.on_signal_settings_param_loaded,
        )
        
    @pyqtSlot()
    def on_app_exit(self):
        """
        Handles application exit by stopping all containers and quitting the app.
        """
        logger.info("Exiting application...")
        self._main_model.ros2_launch_container_model.remove_all_launch_containers()
        self._app.quit()
        
    @pyqtSlot()
    def on_signal_shutdown_btn_clicked(self):
        """
        Slot method to handle the shutdown button click event.
        """
        logger.info("Shutdown button clicked.")
        
    @pyqtSlot()
    def on_signal_restart_btn_clicked(self):
        """
        Slot method to handle the restart button click event.
        """
        logger.info("Restart button clicked.")
    
    @pyqtSlot(str)
    def on_signal_bringup_btn_clicked(self, cmd: str):
        """
        Slot method to handle the bringup button click event.
        """
        logger.info(f"Bringup button clicked with command: {cmd}")
        if cmd == "start":
            self._main_model.ros2_launch_container_model.request_start_container(
                key="bringup"
            )
        elif cmd == "stop":
            self._main_model.ros2_launch_container_model.request_stop_container(
                key="bringup"
            )
            
    @pyqtSlot(str)
    def on_signal_localization_btn_clicked(self, cmd: str):
        """
        Slot method to handle the localization button click event.
        """
        logger.info(f"Localization button clicked with command: {cmd}")
        if cmd == "start":
            self._main_model.ros2_launch_container_model.request_start_container(
                key="localization")
        elif cmd == "stop":
            self._main_model.ros2_launch_container_model.request_stop_container(
                key="localization")
    
    @pyqtSlot(str)
    def on_signal_navigation_wp_follow_btn_clicked(self, cmd: str):
        """
        Slot method to handle the navigation waypoint follow button click event.
        """
        logger.info(f"Navigation waypoint follow button clicked with command: {cmd}")
        if cmd == "start":
            self._main_model.ros2_launch_container_model.request_start_container(
                key="navigation_wp_follow")
        elif cmd == "stop":
            self._main_model.ros2_launch_container_model.request_stop_container(
                key="navigation_wp_follow")
        
    @pyqtSlot(str, str)
    def on_signal_container_status_updated(self, key: str, status: str):
        """
        Slot method to handle container status updates.
        """
        logger.debug(f"Container {key} status updated: {status}")
        
        # Map container keys to view signal methods
        container_map = {
            "bringup": self._main_view.on_signal_bringup_container_status,
            "localization": self._main_view.on_signal_localization_container_status,
            "navigation_wp_follow": self._main_view.on_signal_navigation_container_status
        }
        
        # Map container status to UI status
        status_map = {
            "running": "started",
            "exited": "stopped"
        }
        
        if status not in status_map:
            return
        
        # Update the UI if we have a mapping for this container and status
        if key in container_map and status in status_map:
            container_map[key](status_map[status])
            
        if key == "bringup":
            if status_map[status] == "started" and self._main_model.foxglove_ws_model.is_running() is False:
                self._main_model.foxglove_ws_model.start()
            elif status_map[status] == "stopped" and self._main_model.foxglove_ws_model.is_running() is True:
                self._main_model.foxglove_ws_model.stop()
                
                
    @pyqtSlot(str, dict)
    def on_signal_log_save_btn_clicked(self, save_path: str, waypoints: dict):
        """
        Slot method to handle the save waypoint button click event.
        """
        # replace heading with yaw
        for waypoint in waypoints["waypoints"]:
            if "heading" in waypoint:
                waypoint["yaw"] = waypoint.pop("heading")
                
        # logger.info(f"Save waypoint button clicked with path: {save_path}")
        # logger.info(f"Waypoints: {waypoints}")
        
        self._main_model.save_yaml_waypoints(
            waypoints=waypoints,
            file_path=save_path,
        )
        
    @pyqtSlot(str)
    def on_signal_load_waypoints_btn_clicked(self, file_path: str):
        """
        Slot method to handle the load waypoints button click event.
        """
        logger.info(f"Load waypoints button clicked with path: {file_path}")
        self._main_model.load_yaml_waypoints_file(
            file_path=file_path,
        )
        
    @pyqtSlot(str)
    def on_signal_load_params_btn_clicked(self, file_path: str):
        """
        Slot method to handle the load params button click event.
        """
        logger.info(f"Load params button clicked with path: {file_path}")
        self._main_model.load_yaml_params_file(
            file_path=file_path,
        )
        
    @pyqtSlot(str)
    def on_signal_settings_load_btn_clicked(self, file_path: str):
        """
        Slot method to handle the load settings button click event.
        """
        logger.info(f"Load settings button clicked with path: {file_path}")
        yaml_data = self._main_model.load_yaml_param_settings_file(
            file_path=file_path,
        )
        
        if yaml_data is None:
            logger.error(f"Error loading YAML file {file_path}")
            return None
        
        self._main_model.signal_on_settings_param_loaded.emit(
            file_path, yaml_data,
        )
        
    @pyqtSlot(str, dict)
    def on_signal_settings_save_btn_clicked(self, file_path: str, yaml_data: dict):
        """
        Slot method to handle the save settings button click event.
        """
        logger.info(f"Save settings button clicked with path: {file_path} and data: {yaml_data}")
        self._main_model.save_yaml_param_settings_file(
            file_path=file_path,
            yaml_data=yaml_data,
        )
        
        
                
        
        
        
            
            

        
        
        
        


