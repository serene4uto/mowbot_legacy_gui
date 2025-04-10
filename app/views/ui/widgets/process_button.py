
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QProcess


class ProcessButton(QPushButton):
    def __init__(self, start_script=None, stop_script=None):
        super().__init__()
        
        self.start_script = start_script
        self.stop_script = stop_script

        self.start_proc = QProcess(self)
        self.stop_proc = QProcess(self)

        # self.start_proc.setProcessChannelMode(QProcess.MergedChannels)
        # self.stop_proc.setProcessChannelMode(QProcess.MergedChannels)

        self.start_proc.started.connect(self.on_start_process_started)
        self.start_proc.finished.connect(self.on_start_process_finished)

        self.stop_proc.started.connect(self.on_stop_process_started)
        self.stop_proc.finished.connect(self.on_stop_process_finished)

    
    def start_process(self):
        if self.start_script is None:
            return
        
        self.start_proc.start(
            "/bin/bash",
            [self.start_script],
        )

    def stop_process(self):
        if self.stop_script is None:
            return
        
        self.stop_proc.start(
            "/bin/bash",
            [self.stop_script],
        )

    def on_start_process_started(self):
        pass
    
    def on_start_process_finished(self):
        pass

    def on_stop_process_started(self):
        self.setEnabled(False)
    
    def on_stop_process_finished(self):
        self.setEnabled(True)