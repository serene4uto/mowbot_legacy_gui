# main_model.py

from .foxglove_ws_model import FoxgloveWsModel
from .ros2_launch_container_model import ROS2LaunchContainerModel

class MainModel:
    """
    MainModel aggregates all application models.
    """
    def __init__(self, config):
        """
        Initializes MainModel with the provided configuration.
        
        Args:
            config (dict): Configuration dictionary containing application settings.
        """
        self._config = config
        self._foxglove_ws_model = FoxgloveWsModel.get_instance(
            config=self._config,
        )
        self._ros2_launch_container_model = ROS2LaunchContainerModel.get_instance(
            config=self._config,
        )
        
    @property
    def foxglove_ws_model(self):
        """
        Returns the Foxglove WebSocket model.
        """
        return self._foxglove_ws_model
    
    @property
    def ros2_launch_container_model(self):
        """
        Returns the ROS2 Launch Container model.
        """
        return self._ros2_launch_container_model

