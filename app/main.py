import os
os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--no-sandbox --disable-gpu'

import sys
import logging
import argparse

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt

from app.app_info import __appname__
from app.views import MainWindow
from app.config import get_config
from app import configs as mowbot_configs
from app.utils.logger import logger, ColoredFormatter, ColoredLogger

from app.views import MainView
from app.controllers import MainController
from app.models import MainModel

def main():
    """App entry point."""

    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "--logger-level",
        default="info",
        choices=["debug", "info", "warning", "fatal", "error"],
        help="logger level",
    )
    default_config_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "configs",
        "mowbot_app.yaml",
    )
    parser.add_argument(
        "--config",
        dest="config",
        help=(
            "config file or yaml-format string (default:"
            f" {default_config_file})"
        ),
        default=default_config_file,
    )
    
    
    args = parser.parse_args()
    
    # Set up the logger
    logger.setLevel(getattr(logging, args.logger_level.upper()))
    if not logger.hasHandlers():
        # This block ensures that the logger has a handler after class change
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = ColoredFormatter(ColoredLogger.FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    config_from_args = args.__dict__
    config_file_or_yaml = config_from_args.pop("config")
    mowbot_configs.current_config_file = config_file_or_yaml
    
    config = get_config(config_file_or_yaml, config_from_args)
    
    logger.info(f"Using config: {config}")
    
    # Enable scaling for high dpi screens
    QtWidgets.QApplication.setAttribute(
        QtCore.Qt.AA_EnableHighDpiScaling, True
    )  # enable highdpi scaling
    QtWidgets.QApplication.setAttribute(
        QtCore.Qt.AA_UseHighDpiPixmaps, True
    )  # use highdpi icons
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)

    # Create the Qt app
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(__appname__)
    
    window = MainWindow(
        config=config
    )
    
    controller = MainController(
        config=config,
        app=app,
        main_view=window.main_view,
        main_model=MainModel(
            config=config
        ),
    )
    
    # Remove window title bar/frame
    window.setWindowFlags(Qt.FramelessWindowHint)
        
    # Make window full screen
    window.showFullScreen()
    # window.showMaximized()
    window.raise_() # Bring the window to the front
    
    # Set the window to be non-resizable
    # window.setFixedSize(window.size())
    
    # Run the app
    sys.exit(app.exec())


if __name__ == '__main__':
    main()