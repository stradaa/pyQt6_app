import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QFileDialog, QLabel, QPushButton
)

###############################################################################
# StartupDialog
###############################################################################
class StartupDialog(QDialog):
    """
    A simple dialog to prompt the user to load a folder or file before
    launching the main application GUI.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_path = None
        self.setWindowTitle("Select Dataset")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        info_label = QLabel(
            "Welcome to GraFT-App! Please select either a folder or file\n"
            "to load your dataset."
        )
        layout.addWidget(info_label)

        # Buttons to load folder or file
        button_layout = QHBoxLayout()
        load_folder_btn = QPushButton("Load Folder")
        load_folder_btn.clicked.connect(self.on_load_folder)
        load_file_btn = QPushButton("Load File")
        load_file_btn.clicked.connect(self.on_load_file)

        button_layout.addWidget(load_folder_btn)
        button_layout.addWidget(load_file_btn)
        layout.addLayout(button_layout)

        # Optionally add a "Cancel" button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)

        self.setLayout(layout)

    def on_load_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.selected_path = folder_path
            self.accept()

    def on_load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "",
            "Data Files (*.h5 *.mat *.tiff *.tif);;All Files (*)"
        )
        if file_path:
            self.selected_path = file_path
            self.accept()