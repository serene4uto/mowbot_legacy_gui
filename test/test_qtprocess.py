#!/usr/bin/env python3
import sys
import logging
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import QProcess

# Set up basic logging to the console
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ProcessButtonWidget(QPushButton):
    def __init__(self, start_script=None, stop_script=None):
        # Set the button text initially
        super().__init__("Run Start Script")
        
        self.start_script = start_script
        self.stop_script = stop_script

        self.start_proc = QProcess(self)
        self.stop_proc = QProcess(self)

        # Merge standard output and error channels for easier debugging.
        self.start_proc.setProcessChannelMode(QProcess.MergedChannels)

        # Connect signals for the start process.
        self.start_proc.started.connect(self.on_start_process_started)
        self.start_proc.finished.connect(self.on_start_process_finished)
        self.start_proc.readyReadStandardOutput.connect(self.handle_stdout)
        self.start_proc.readyReadStandardError.connect(self.handle_stderr)
        self.start_proc.errorOccurred.connect(self.handle_error)

        # Connect signals for the stop process.
        self.stop_proc.started.connect(self.on_stop_process_started)
        self.stop_proc.finished.connect(self.on_stop_process_finished)

        # When the button is clicked, start the process.
        self.clicked.connect(self.start_process)

    def start_process(self):
        if self.start_script is None:
            logger.error("No start_script provided.")
            return
        logger.info("Starting process...")
        self.start_proc.start("/bin/bash", [self.start_script])

    def stop_process(self):
        if self.stop_script is None:
            logger.error("No stop_script provided.")
            return
        logger.info("Stopping process...")
        self.stop_proc.start("/bin/bash", [self.stop_script])

    def on_start_process_started(self):
        logger.info("Start process initiated.")

    def on_start_process_finished(self, exitCode, exitStatus):
        logger.info(f"Start process finished with exitCode={exitCode} exitStatus={exitStatus}")

    def handle_stdout(self):
        data = self.start_proc.readAllStandardOutput().data().decode()
        logger.info("STDOUT: " + data)

    def handle_stderr(self):
        data = self.start_proc.readAllStandardError().data().decode()
        logger.error("STDERR: " + data)

    def handle_error(self, error):
        logger.error("Process error: " + str(error))

    def on_stop_process_started(self):
        logger.info("Stop process initiated.")
        self.setEnabled(False)

    def on_stop_process_finished(self, exitCode, exitStatus):
        logger.info(f"Stop process finished with exitCode={exitCode} exitStatus={exitStatus}")
        self.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Process Button Test")

    layout = QVBoxLayout(window)
    
    # Adjust these paths as necessary. 
    # Create a simple bash script (test_start.sh) in the same folder with executable permissions.
    start_script = "./test_start.sh"
    stop_script = None  # Use a stop script if needed, or leave as None.

    process_button = ProcessButtonWidget(start_script=start_script, stop_script=stop_script)
    layout.addWidget(process_button)

    window.setLayout(layout)
    window.resize(300, 100)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
