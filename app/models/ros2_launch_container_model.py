# ros2_launch_container_model.py

import os
import docker
import json
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread, pyqtSlot
from app.models.ros2_launch_container_cfg import CONTAINERS_CFG
from app.utils.logger import logger

class ROS2LaunchContainerModel(QObject):
    """
    Model for managing ROS2 launch containers via Docker.
    Provides methods to create, start, stop, remove, and check container statuses.
    Emits signal_container_status_updated for status changes.
    Also supports periodic tasks through worker timers.
    """
    signal_container_status_updated = pyqtSignal(str, str)  # key, status
    

    _instance = None

    @staticmethod
    def get_instance(config) -> 'ROS2LaunchContainerModel':
        if ROS2LaunchContainerModel._instance is None:
            ROS2LaunchContainerModel._instance = ROS2LaunchContainerModel(config)
        return ROS2LaunchContainerModel._instance

    def __init__(self, 
            config
        ):
        if ROS2LaunchContainerModel._instance is not None:
            raise Exception("This class is a singleton! Use get_instance() instead.")
        super().__init__()
        self._config = config
        try:
            self.docker_client = docker.from_env()
            self.docker_client.ping()  # Test Docker connection.
            logger.info("Docker connection established.")
        except docker.errors.DockerException as e:
            raise RuntimeError(f"Failed to connect to Docker: {e}")
        self.containers_config = CONTAINERS_CFG

        # Worker and thread attributes for periodic tasks.
        self._container_manage_worker = None
        self._worker_thread = None

    def create_launch_container(self, key: str):
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
                privileged=config["privileged"],
                volumes=config["volumes"],
                environment=config["environment"],
                network=config["network_mode"],
                detach=config["detach"],
                tty=config["tty"],
            )
            
    def create_all_launch_containers(self) -> None:
        """
        Creates all launch containers defined in the configuration.
        """
        for key in self.containers_config.keys():
            self.create_launch_container(key=key)
            logger.info(f"Created container: {key}")

    def start_launch_container(self, key: str) -> None:
        container = self.create_launch_container(key)
        if container.status != "running":
            container.start()
            logger.info(f"Started container: {key}")
        else:
            logger.info(f"Container {key} is already running.")

    def stop_launch_container(self, key: str, timeout: int = 10) -> None:
        try:
            name = self.containers_config[key]["name"]
            container = self.docker_client.containers.get(name)
            container.stop(timeout=timeout)
            logger.info(f"Stopped container: {key}")
        except docker.errors.NotFound:
            logger.warning(f"Container not found: {key}")
            
    def stop_all_launch_containers(self, timeout: int = 10) -> None:
        for key in self.containers_config.keys():
            self.stop_launch_container(key=key, timeout=timeout)

    def get_launch_container_status(self, key: str) -> str:
        try:
            name = self.containers_config[key]["name"]
            container = self.docker_client.containers.get(name)
            return container.status
        except docker.errors.NotFound:
            return "not created"

    def check_launch_container(self, key: str) -> None:
        status = self.get_launch_container_status(key)
        self.signal_container_status_updated.emit(key, status)

    def check_all_launch_containers(self) -> None:
        for key in self.containers_config.keys():
            self.check_launch_container(key)

    def remove_launch_container(self, key: str) -> None:
        try:
            name = self.containers_config[key]["name"]
            container = self.docker_client.containers.get(name)
            container.remove(force=True)
            logger.info(f"Removed container: {key}")
        except docker.errors.NotFound:
            logger.warning(f"Container not found for removal: {key}")
            
    def remove_all_launch_containers(self) -> None:
        for key in self.containers_config.keys():
            self.remove_launch_container(key=key)
            logger.info(f"Removed container: {key}")

    # --- Periodic Task Management ---
    def start_periodic_tasks(self, status_interval_ms: int = 1000, container_interval_ms: int = 1000):
        """
        Starts a worker thread that handles two periodic tasks:
          1. Periodically checks all launch container statuses.
          2. Processes start/stop container requests.
        """
        if self._container_manage_worker is None:
            self._container_manage_worker = _ContainerManageWorker(
                model=self, 
                status_interval=status_interval_ms, 
                container_interval=container_interval_ms
            )
            self._worker_thread = QThread()
            self._container_manage_worker.moveToThread(self._worker_thread)
            self._worker_thread.started.connect(self._container_manage_worker.start_timers)
            self._worker_thread.start()
            logger.info("Periodic tasks started.")

    def stop_periodic_tasks(self):
        """
        Stops the worker thread handling the periodic tasks.
        """
        if self._container_manage_worker:
            self._container_manage_worker.stop_timers()
            self._worker_thread.quit()
            self._worker_thread.wait()
            logger.info("Periodic tasks stopped.")
            self._container_manage_worker = None
            self._worker_thread = None

    # --- Slots to trigger start/stop container actions from external signals ---
    @pyqtSlot(str)
    def on_signal_start_container(self, key: str):
        """
        Slot to handle external signals requesting container start.
        Forwards the key to the worker.
        """
        logger.info(f"Received signal to start container: {key}")
        if self._container_manage_worker:
            self._container_manage_worker.enqueue_start(key)

    @pyqtSlot(str)
    def on_signal_stop_container(self, key: str):
        """
        Slot to handle external signals requesting container stop.
        Forwards the key to the worker.
        """
        logger.info(f"Received signal to stop container: {key}")
        if self._container_manage_worker:
            self._container_manage_worker.enqueue_stop(key)
            
    def request_start_container(self, key: str):
        """
        Requests to start a container by emitting a signal.
        This method is called from the UI or other components.
        """
        logger.info(f"Requesting to start container: {key}")
        self.on_signal_start_container(key)
        
    def request_stop_container(self, key: str):
        """
        Requests to stop a container by emitting a signal.
        This method is called from the UI or other components.
        """
        logger.info(f"Requesting to stop container: {key}")
        self.on_signal_stop_container(key)
        
    def request_stop_all_containers(self):
        """
        Requests to stop all containers by emitting a signal.
        This method is called from the UI or other components.
        """
        logger.info("Requesting to stop all containers.")
        for key in self.containers_config.keys():
            self.on_signal_stop_container(key)


class _ContainerManageWorker(QObject):
    """
    Worker class running in a separate QThread to periodically perform tasks:
      - Check the status of all launch containers.
      - Process queued start/stop container requests.
    """
    def __init__(self, model: ROS2LaunchContainerModel, status_interval: int, container_interval: int, parent=None):
        super().__init__(parent)
        self.model = model
        self.status_interval = status_interval
        self.container_interval = container_interval

        # Timer for checking container statuses.
        self.status_timer = QTimer(self)
        self.status_timer.setInterval(self.status_interval)
        self.status_timer.timeout.connect(self.perform_status_check)

        # Timer for processing container start/stop requests.
        self.container_process_timer = QTimer(self)
        self.container_process_timer.setInterval(self.container_interval)
        self.container_process_timer.timeout.connect(self.perform_container_process_task)

        # Queues for pending start and stop requests.
        self.start_queue = []
        self.stop_queue = []

    @pyqtSlot()
    def start_timers(self):
        self.status_timer.start()
        self.container_process_timer.start()

    @pyqtSlot()
    def stop_timers(self):
        self.status_timer.stop()
        self.container_process_timer.stop()

    @pyqtSlot()
    def perform_status_check(self):
        """Periodically check all container statuses."""
        self.model.check_all_launch_containers()

    @pyqtSlot()
    def perform_container_process_task(self):
        """
        Processes queued container start and stop requests.
        """
        # Process all start requests.
        while self.start_queue:
            key = self.start_queue.pop(0)
            self.model.start_launch_container(key=key)
        # Process all stop requests.
        while self.stop_queue:
            key = self.stop_queue.pop(0)
            self.model.stop_launch_container(
                key=key, timeout=self.model._config["container_stop_timeout"])
    
    def enqueue_start(self, key: str):
        """Adds a container start request to the queue."""
        if key not in self.start_queue:
            self.start_queue.append(key)
    
    def enqueue_stop(self, key: str):
        """Adds a container stop request to the queue."""
        if key not in self.stop_queue:
            self.stop_queue.append(key)
