# main_controller.py
from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
    pyqtSlot,
    QTimer,
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
        self._main_view = main_view
        self._main_model = main_model
        
        self._main_model.ros2_launch_container_model.start_periodic_tasks(
            status_interval_ms=1000,
            container_interval_ms=1000,
        )
        
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
        
        # Container status update signals
        self._main_model.ros2_launch_container_model.signal_container_status_updated.connect(
            self.on_signal_container_status_updated,
        )
            
    
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
        
        # Update the UI if we have a mapping for this container and status
        if key in container_map and status in status_map:
            container_map[key](status_map[status])
            
        if key == "bringup":
            if status_map[status] == "started" \
            and self._main_model.foxglove_ws_model.is_running() is False:
                self._main_model.foxglove_ws_model.start()
            elif status_map[status] == "stopped" \
            and self._main_model.foxglove_ws_model.is_running() is True:
                self._main_model.foxglove_ws_model.stop()
            
            

        
        
        
        


