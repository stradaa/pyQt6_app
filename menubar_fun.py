import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QMainWindow, QWidget, QTabWidget, QVBoxLayout, 
    QHBoxLayout, QFileDialog, QLabel, QPushButton
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from v3 import *

def open_dataset(self):
    """
    Launch a new StartupDialog to pick a folder or file,
    then open a NEW main window for that dataset.
    """
    dialog = StartupDialog(self)
    result = dialog.exec()

    # If the user picks a file/folder and clicks OK
    if result == QDialog.DialogCode.Accepted and dialog.selected_path:
        new_window = CaImagingApp(data_path=dialog.selected_path)
        new_window.show()
        # Keep a reference so the new window isn't garbage-collected
        # or store it in a global list, etc.
        # For example:
        if not hasattr(self, '_open_projects'):
            self._open_projects = []
        self._open_projects.append(new_window)