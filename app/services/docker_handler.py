# import os
# import docker
# from PyQt5.QtCore import QObject, pyqtSignal

# from app.services.docker_container_config import CONTAINER_CFG, IMAGE

# from app.utils.logger import logger
    

# class DockerHandler(QObject):
#     """
#     Singleton class to handle Docker container operations.
#     """
    
#     _instance = None
    
#     @staticmethod
#     def get_instance():
#         """
#         Returns the singleton instance of DockerHandler.
#         """
#         if not hasattr(DockerHandler, "_instance"):
#             DockerHandler._instance = DockerHandler()
#         return DockerHandler._instance
    
    
#     def __init__(
#         self,
#         config=None,
#     ):
#         """
#         Initializes the DockerHandler instance.
#         """
        
#         if DockerHandler._instance is not None:
#             raise Exception("This class is a singleton! Use get_instance() instead.")
#         super().__init__()
        
#         self._config = config
        
#         self.docker_client = docker.from_env()
        
#         self.containers = {}  # Store container tasks by name
        
#         try:
#             self.docker_client = docker.from_env()
#             # Test connection
#             self.docker_client.ping()
#         except docker.errors.DockerException as e:
#             raise RuntimeError(f"Failed to connect to Docker: {e}")
        
    
#     def _start_container(self, container_name):
        
        
        
        
        
        
        
        
        
#     def start(self):
#         pass
        
        
        
        
        
        
    