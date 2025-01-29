import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QMainWindow, QWidget, QTabWidget, QVBoxLayout, 
    QHBoxLayout, QFileDialog, QLabel, QPushButton
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

################################################################################
# 1) StartupDialog
################################################################################
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

        info_label = QLabel("Welcome! Please select either a folder or file\n"
                            "to load your dataset.")
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
            self, "Select File",
            "", "Data Files (*.h5 *.mat *.tiff *.tif);;All Files (*)"
        )
        if file_path:
            self.selected_path = file_path
            self.accept()

################################################################################
# 2) Individual tabs
################################################################################
class PreprocessingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Preprocessing Steps:"))

        crop_button = QPushButton("Crop")
        crop_button.clicked.connect(self.crop_data)
        layout.addWidget(crop_button)

        mask_button = QPushButton("Mask Selection")
        mask_button.clicked.connect(self.mask_selection)
        layout.addWidget(mask_button)

        motion_button = QPushButton("Motion Correction")
        motion_button.clicked.connect(self.motion_correction)
        layout.addWidget(motion_button)

        wavelet_button = QPushButton("Wavelet Denoising")
        wavelet_button.clicked.connect(self.wavelet_denoising)
        layout.addWidget(wavelet_button)

        layout.addStretch()
        self.setLayout(layout)

    def crop_data(self):
        print("[Preprocessing] Cropping data...")

    def mask_selection(self):
        print("[Preprocessing] Selecting mask...")

    def motion_correction(self):
        print("[Preprocessing] Performing motion correction...")

    def wavelet_denoising(self):
        print("[Preprocessing] Applying wavelet denoising...")

class ParameterSetupTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Parameter setup goes here."))
        layout.addStretch()
        self.setLayout(layout)

class AlgorithmExecutionTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Algorithm Execution"))
        run_button = QPushButton("Run Algorithm")
        run_button.clicked.connect(self.run_algorithm)
        layout.addWidget(run_button)
        layout.addStretch()
        self.setLayout(layout)

    def run_algorithm(self):
        print("[Algorithm] Running main analysis...")

class ResultsVisualizationTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Results Visualization"))
        layout.addStretch()
        self.setLayout(layout)

################################################################################
# 3) Main Window (CaImagingApp)
################################################################################
class CaImagingApp(QMainWindow):
    """
    Main Application Window.
    Initialized with a data_path from the StartupDialog.
    """
    def __init__(self, data_path=None, parent=None):
        super().__init__(parent)
        self.data_path = data_path
        self.setWindowTitle("Calcium Imaging GUI")

        self.setMinimumSize(1000, 600)
        self.setStyleSheet(self._get_modern_style())

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Create tabs
        self.preprocess_tab = PreprocessingTab()
        self.parameter_tab = ParameterSetupTab()
        self.algorithm_tab = AlgorithmExecutionTab()
        self.results_tab = ResultsVisualizationTab()

        # Add tabs
        self.tab_widget.addTab(self.preprocess_tab, "Preprocessing")
        self.tab_widget.addTab(self.parameter_tab, "Parameter Setup")
        self.tab_widget.addTab(self.algorithm_tab, "Algorithm Execution")
        self.tab_widget.addTab(self.results_tab, "Results Visualization")

        # Create a menu bar
        self._create_menu_bar()

        # Immediately load data if path is provided
        if self.data_path:
            self.load_data(self.data_path)

    def _get_modern_style(self):
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: #ffffff;
            }
            QTabBar::tab {
                background: #e0e0e0;
                padding: 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                font-weight: bold;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #005aaa;
            }
            QMenuBar {
                background-color: #e0e0e0;
                color: #000000;
            }
            QMenuBar::item {
                background-color: #e0e0e0;
                color: #000000;
            }
            QMenuBar::item:selected {
                background-color: #cacaca;
            }
            QMenu {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
            }
            QMenu::item:selected {
                background-color: #f0f0f0;
            }
        """

    def _create_menu_bar(self):
        menubar = self.menuBar()
        # file menu
        file_menu = menubar.addMenu("File")
        open_action = QAction("Open Another Dataset", self)
        open_action.triggered.connect(self.open_dataset)
        file_menu.addAction(open_action)

        # view menu
        view_menu = menubar.addMenu("View")
        view_action = QAction("Appearance", self)
        # view_action.triggered.connect(self.view_action)
        view_menu.addAction(view_action)

        # edit menu
        edit_menu = menubar.addMenu("Edit")
        # go menu
        go_menu = menubar.addMenu("Go")
        # help menu
        help_menu = menubar.addMenu("Help")


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


    def load_data(self, data_path):
        print(f"[MainApp] Loading data from: {data_path}")
        # Insert your file loading logic here

################################################################################
# 4) The main() function
################################################################################
def main():
    app = QApplication(sys.argv)

    # Show the initial startup dialog for the user to select data
    dialog = StartupDialog()
    dialog_result = dialog.exec()

    if dialog_result == QDialog.DialogCode.Accepted and dialog.selected_path:
        # They picked a file/folder -> create the main window
        window = CaImagingApp(data_path=dialog.selected_path)
        window.show()
        sys.exit(app.exec())
    else:
        # They canceled or closed the dialog without picking -> exit
        sys.exit(0)

if __name__ == "__main__":
    main()
