# main_controller.py
from PyQt5.QtCore import QObject

from app.views import MainView
from app.models import MainModel
from app.utils.logger import logger

class MainController(QObject):
    """
    MainController is responsible for managing the main view and its interactions with the model.
    """
    def __init__(
        self, 
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
        
        self._main_view = main_view
        self._main_model = main_model

        
        
        
        


