import os
import docker
from PyQt5.QtCore import QObject, pyqtSignal

from app.services.ros2_launch_container_cfg import CONTAINERS_CFG
from app.utils.logger import logger

class ROS2LaunchContainerManager(QObject):
    
    signal_status_updated = pyqtSignal(str, str)  # key, status
    
    _instance = None
    
    @staticmethod
    def get_instance():
        """
        Returns the singleton instance of ROS2LaunchContainerManager.
        """
        if ROS2LaunchContainerManager._instance is None:
            ROS2LaunchContainerManager._instance = ROS2LaunchContainerManager()
        return ROS2LaunchContainerManager._instance
    
    def __init__(self, config=None):
        """
        Initializes the ROS2LaunchContainerManager instance.
        """
        if ROS2LaunchContainerManager._instance is not None:
            raise Exception("This class is a singleton! Use get_instance() instead.")
        super().__init__()
        self._config = config
        
        try:
            self.docker_client = docker.from_env()
            self.docker_client.ping()  # Test Docker connection
        except docker.errors.DockerException as e:
            raise RuntimeError(f"Failed to connect to Docker: {e}")
        
        self.containers_config = CONTAINERS_CFG
        
    def create_launch_container(self, key):
        """
        Retrieves the container if it exists; otherwise creates it.
        """
        config = self.containers_config[key]
        name = config["name"]
        try:
            return self.docker_client.containers.get(name)
        except docker.errors.NotFound:
            logger.info(f"Creating container: {name}")
            return self.docker_client.containers.create(
                image=config["image"],
                name=name,
                command=config["command"],
                volumes=config.get("volumes", {}),
                environment=config.get("environment", {}),
                network=config.get("network", "host"),
                detach=True,
                tty=True
            )
    
    def start_launch_container(self, key):
        """
        Starts the container associated with the provided key.
        """
        container = self.create_launch_container(key)
        # Check the container's current status
        if container.status != "running":
            container.start()
            logger.info(f"Started container: {key}")
        else:
            logger.info(f"Container {key} is already running.")
    
    def stop_launch_container(self, key, timeout=10):
        """
        Stops the container associated with the provided key.
        """
        try:
            name = self.containers_config[key]["name"]
            container = self.docker_client.containers.get(name)
            container.stop(timeout=timeout)
            logger.info(f"Stopped container: {key}")
        except docker.errors.NotFound:
            logger.warning(f"Container not found: {key}")
    
    def get_launch_container_status(self, key):
        """
        Returns the current status of the container.
        """
        try:
            name = self.containers_config[key]["name"]
            container = self.docker_client.containers.get(name)
            return container.status
        except docker.errors.NotFound:
            return "not created"
        
    def check_launch_container(self, key):
        """
        Emits the current container status through signal_status_updated.
        """
        status = self.get_launch_container_status(key)
        self.signal_status_updated.emit(key, status)
    
    def remove_launch_container(self, key):
        """
        Removes the container from Docker.
        Uses force removal to ensure cleanup even if the container is running.
        """
        try:
            name = self.containers_config[key]["name"]
            container = self.docker_client.containers.get(name)
            container.remove(force=True)
            logger.info(f"Removed container: {key}")
        except docker.errors.NotFound:
            logger.warning(f"Container not found for removal: {key}")
