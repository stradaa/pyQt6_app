import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QFileDialog,
    QLabel, QPushButton, QListWidget, QFrame
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSettings

###############################################################################
# StartupDialog
###############################################################################
class StartupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_path = None
        self.settings = QSettings("GraFT-App", "StartupDialog")  # Unique app identifier
        self.setWindowTitle("Welcome to GraFT-App")
        self.setFixedSize(500, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Banner at the top
        banner_label = QLabel()
        # banner_pixmap = QPixmap("graft_logo_v2.png")  # Replace with your banner image
        banner_pixmap = QPixmap("temp_dialog.jpg")
        banner_label.setPixmap(banner_pixmap.scaledToWidth(480, Qt.TransformationMode.SmoothTransformation))
        banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(banner_label)

        # Recent Files Section
        recent_files_label = QLabel("Recent Files")
        recent_files_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(recent_files_label)
        
        self.recent_files_list = QListWidget()
        self.load_recent_files()  # Populate recent files
        layout.addWidget(self.recent_files_list)
        
        # Horizontal line separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Buttons to load folder or file
        button_layout = QHBoxLayout()
        load_folder_btn = QPushButton("Load Folder")
        load_folder_btn.clicked.connect(self.on_load_folder)
        load_file_btn = QPushButton("Load File")
        load_file_btn.clicked.connect(self.on_load_file)

        button_layout.addWidget(load_folder_btn)
        button_layout.addWidget(load_file_btn)
        layout.addLayout(button_layout)

        # Bottom Buttons (Cancel and Open)
        bottom_buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        open_button = QPushButton("Open")
        open_button.clicked.connect(self.on_recent_file_selected)
        open_button.setEnabled(False)  # Disabled initially until a file is selected
        
        bottom_buttons_layout.addWidget(cancel_button)
        bottom_buttons_layout.addWidget(open_button)
        layout.addLayout(bottom_buttons_layout)
        
        self.setLayout(layout)
        
        # Enable Open button when a file is selected
        self.recent_files_list.itemSelectionChanged.connect(
            lambda: open_button.setEnabled(bool(self.recent_files_list.selectedItems()))
        )

    def load_recent_files(self):
        """Load the recent files list from settings."""
        recent_files = self.settings.value("recentFiles", [])
        self.recent_files_list.clear()
        self.recent_files_list.addItems(recent_files)

    def save_recent_file(self, file_path):
        """Save the selected file to the recent files list."""
        recent_files = self.settings.value("recentFiles", [])
        if file_path in recent_files:
            recent_files.remove(file_path)  # Move to top if it already exists
        recent_files.insert(0, file_path)
        recent_files = recent_files[:3]  # Keep only the last 3 entries
        self.settings.setValue("recentFiles", recent_files)
        self.load_recent_files()  # Refresh the list

    def on_recent_file_selected(self):
        """Handles when a user selects a file from recent files and clicks Open."""
        selected_item = self.recent_files_list.currentItem()
        if selected_item:
            self.selected_path = selected_item.text()  # Store the selected path
            self.accept()  # Close the dialog

    def on_load_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.save_recent_file(folder_path)
            self.selected_path = folder_path
            self.accept()

    def on_load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "",
            "Data Files (*.h5 *.mat *.tiff *.tif *.nwb);;All Files (*)"
        )
        if file_path:
            self.save_recent_file(file_path)
            self.selected_path = file_path
            self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = StartupDialog()
    if dialog.exec():
        print(f"Selected Path: {dialog.selected_path}")