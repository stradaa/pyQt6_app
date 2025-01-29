import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, 
    QHBoxLayout, QMenuBar, QMenu, QFileDialog, QLabel, QPushButton
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt


class PreprocessingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Example Buttons for different preprocessing steps
        crop_button = QPushButton("Crop")
        crop_button.clicked.connect(self.crop_data)

        mask_button = QPushButton("Mask Selection")
        mask_button.clicked.connect(self.mask_selection)

        motion_button = QPushButton("Motion Correction")
        motion_button.clicked.connect(self.motion_correction)

        wavelet_button = QPushButton("Wavelet Denoising")
        wavelet_button.clicked.connect(self.wavelet_denoising)

        layout.addWidget(QLabel("Preprocessing Steps:"))
        layout.addWidget(crop_button)
        layout.addWidget(mask_button)
        layout.addWidget(motion_button)
        layout.addWidget(wavelet_button)
        layout.addStretch()

        self.setLayout(layout)

    def crop_data(self):
        # Placeholder for interactive cropping
        print("Cropping data... (placeholder)")

    def mask_selection(self):
        # Placeholder for manual or semi-automated mask selection
        print("Selecting mask... (placeholder)")

    def motion_correction(self):
        # Placeholder for motion correction
        print("Performing motion correction... (placeholder)")

    def wavelet_denoising(self):
        # Placeholder for wavelet-based denoising
        print("Applying wavelet denoising... (placeholder)")


class ParameterSetupTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Parameter setup goes here."))
        # Add your parameter widgets (QLineEdit, QSpinBox, etc.) as needed

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
        # Placeholder for the core algorithm execution
        print("Running main algorithm... (placeholder)")


class ResultsVisualizationTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Results Visualization"))
        # You can embed matplotlib or pyqtgraph for plotting your results

        layout.addStretch()
        self.setLayout(layout)


class CaImagingApp(QMainWindow):
    """
    Main Window of the application. Each instance corresponds to a new project.
    """
    def __init__(self, data_path=None, parent=None):
        super().__init__(parent)
        self.data_path = data_path
        self.setWindowTitle("Calcium Imaging GUI")

        # Optionally set a minimum size and a more modern style
        self.setMinimumSize(1000, 600)
        self.setStyleSheet(self._get_modern_style())

        # Create a central widget that holds tabs
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

        # Menu bar
        self._create_menu_bar()

    def _get_modern_style(self):
        """
        Returns a stylesheet to give a modern look,
        including styles for the menu bar and menus.
        """
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }
            /* Tab widget */
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
            /* Push buttons */
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #005aaa;
            }
            /* Menu bar */
            QMenuBar {
                background-color: #e0e0e0;   /* or another preferred color */
                color: #000000;             /* text color */
            }
            QMenuBar::item {
                background-color: #e0e0e0;
                color: #000000;
            }
            QMenuBar::item:selected {
                background-color: #cacaca;   /* hover color */
            }
            /* Menus that drop down from the menu bar */
            QMenu {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
            }
            QMenu::item:selected {
                background-color: #f0f0f0;
            }

            QPushButton:hover {
                background-color: #005aaa;
            }
        """


    def _create_menu_bar(self):
        # Create menu bar
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")

        # Load New submenu
        load_new_menu = QMenu("Load New", self)
        load_folder_action = QAction("Folder", self)
        load_folder_action.triggered.connect(self.load_new_folder)

        load_file_action = QAction("File", self)
        load_file_action.triggered.connect(self.load_new_file)

        load_new_menu.addAction(load_folder_action)
        load_new_menu.addAction(load_file_action)

        file_menu.addMenu(load_new_menu)

    def load_new_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            # Create new instance of the GUI
            self._launch_new_project(folder_path)

    def load_new_file(self):
        # You can filter for specific file formats like *.h5, *.mat, *.tiff, etc.
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File",
            "", "Data Files (*.h5 *.mat *.tiff *.tif);;All Files (*)"
        )
        if file_path:
            # Create new instance of the GUI
            self._launch_new_project(file_path)

    def _launch_new_project(self, data_path):
        # This spawns a new instance of CaImagingApp
        self.new_project = CaImagingApp(data_path=data_path)
        self.new_project.show()


def main():
    app = QApplication(sys.argv)
    window = CaImagingApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
