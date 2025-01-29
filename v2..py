import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QMainWindow, QWidget, QTabWidget, QVBoxLayout,
    QHBoxLayout, QFileDialog, QLabel, QPushButton
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, pyqtSignal, QCoreApplication

class StartupDialog(QDialog):
    """
    Dialog to prompt the user to select a folder or file for a new dataset.
    Each successful selection emits pathSelected(path).
    """
    pathSelected = pyqtSignal(str)  # Custom signal

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Dataset")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        info_label = QLabel("Welcome! Please select either a folder or file to load your dataset.\n"
                            "Each selection will open a new window.")
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

        # Optionally add a "Close" or "Cancel" button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def on_load_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            # Emit signal with the chosen path
            self.pathSelected.emit(folder_path)

    def on_load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File",
            "", "Data Files (*.h5 *.mat *.tiff *.tif);;All Files (*)"
        )
        if file_path:
            # Emit signal with the chosen path
            self.pathSelected.emit(file_path)


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
        print("[Preprocessing] Cropping data... (placeholder)")

    def mask_selection(self):
        print("[Preprocessing] Selecting mask... (placeholder)")

    def motion_correction(self):
        print("[Preprocessing] Performing motion correction... (placeholder)")

    def wavelet_denoising(self):
        print("[Preprocessing] Applying wavelet denoising... (placeholder)")


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
        print("[Algorithm] Running main analysis... (placeholder)")


class ResultsVisualizationTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Results Visualization"))
        layout.addStretch()
        self.setLayout(layout)


class CaImagingApp(QMainWindow):
    """
    Main Application Window for a loaded dataset (file or folder).
    """
    def __init__(self, data_path=None, parent=None):
        super().__init__(parent)
        self.data_path = data_path
        self.setWindowTitle("Calcium Imaging GUI")

        # Optionally set a minimum size and a more modern style
        self.setMinimumSize(1000, 600)
        self.setStyleSheet(self._get_modern_style())

        # Create the tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Create and add tabs
        self.preprocess_tab = PreprocessingTab()
        self.parameter_tab = ParameterSetupTab()
        self.algorithm_tab = AlgorithmExecutionTab()
        self.results_tab = ResultsVisualizationTab()

        self.tab_widget.addTab(self.preprocess_tab, "Preprocessing")
        self.tab_widget.addTab(self.parameter_tab, "Parameter Setup")
        self.tab_widget.addTab(self.algorithm_tab, "Algorithm Execution")
        self.tab_widget.addTab(self.results_tab, "Results Visualization")

        # Create menu bar (optional)
        self._create_menu_bar()

        # Load data if a path was provided
        if self.data_path:
            self.load_data(self.data_path)

    def _get_modern_style(self):
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
        file_menu = menubar.addMenu("File")

        # Example "Open Another Dataset" action
        open_action = QAction("Open Another Dataset", self)
        open_action.triggered.connect(self.open_dataset)
        file_menu.addAction(open_action)

    def open_dataset(self):
        """
        If the user wants to open a new dataset in a brand-new window,
        we can re-use the StartupDialog approach or do a direct file/folder open.
        """
        dialog = StartupDialog(self)
        # Reuse the same approach to open new windows
        dialog.pathSelected.connect(self._launch_new_project)
        dialog.exec()

    def _launch_new_project(self, data_path):
        new_window = CaImagingApp(data_path)
        new_window.show()

    def load_data(self, data_path):
        """
        Placeholder logic for reading data. Extend as needed.
        """
        print(f"[MainApp] Loading data from: {data_path}")


def main():
    app = QApplication(sys.argv)
    # Prevent the app from quitting when the StartupDialog closes,
    # so we can keep multiple main windows open
    app.setQuitOnLastWindowClosed(False)

    # Keep references to main windows so they're not garbage-collected
    open_projects = []

    def spawn_main_window(path: str):
        """
        Slot called each time the user picks a dataset in the StartupDialog.
        This creates a new main window for the dataset.
        """
        main_win = CaImagingApp(data_path=path)
        main_win.show()
        open_projects.append(main_win)

    # Create and show the startup dialog
    startup_dialog = StartupDialog()
    # Connect the pathSelected signal to create new main windows
    startup_dialog.pathSelected.connect(spawn_main_window)
    startup_dialog.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
