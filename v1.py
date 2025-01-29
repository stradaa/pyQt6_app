import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QMainWindow, QWidget, QTabWidget, QVBoxLayout, 
    QHBoxLayout, QMenuBar, QMenu, QFileDialog, QLabel, QPushButton
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QCoreApplication

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

        info_label = QLabel("Welcome! Please select either a folder or file\nto load your dataset.")
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
            self.accept()  # Close dialog with "Accepted" status

    def on_load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File",
            "", "Data Files (*.h5 *.mat *.tiff *.tif);;All Files (*)"
        )
        if file_path:
            self.selected_path = file_path
            self.accept()  # Close dialog with "Accepted" status


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
        # Placeholder for interactive cropping
        print("[Preprocessing] Cropping data...")

    def mask_selection(self):
        # Placeholder for manual or semi-automated mask selection
        print("[Preprocessing] Selecting mask...")

    def motion_correction(self):
        # Placeholder for motion correction
        print("[Preprocessing] Performing motion correction...")

    def wavelet_denoising(self):
        # Placeholder for wavelet-based denoising
        print("[Preprocessing] Applying wavelet denoising...")


class ParameterSetupTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Parameter setup goes here."))
        # Add your parameter widgets (QLineEdit, QSpinBox, etc.)
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
        # Placeholder for your main analysis or algorithm
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


class CaImagingApp(QMainWindow):
    """
    Main Application Window.
    Initialized with a data_path from the StartupDialog.
    """
    def __init__(self, data_path=None, parent=None):
        super().__init__(parent)
        self.data_path = data_path
        self.setWindowTitle("Calcium Imaging GUI")

        # Optionally set a minimum size and a more modern style
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

        # Menu bar
        self._create_menu_bar()

        # If a data path was provided, you might want to immediately load it.
        if self.data_path:
            self.load_data(self.data_path)

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
        """

    def _create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        # Optional 'Reload' or 'Open' action if user wants to switch data again
        open_action = QAction("Open Another Dataset", self)
        open_action.triggered.connect(self.open_dataset)

        file_menu.addAction(open_action)

    def open_dataset(self):
        """
        If you want to allow switching data within the already opened app,
        you could reuse the logic or pop up a StartupDialog again.
        """
        print('HERE ALEX')
        main()
        # dialog = StartupDialog(self)
        # if dialog.exec() == QDialog.DialogCode.Accepted:
        #     new_data_path = dialog.selected_path
        #     if new_data_path:
        #         self.load_data(new_data_path)

    def load_data(self, data_path):
        """
        Load your data from the specified path.
        Use your existing data-handling logic here.
        """
        print(f"[MainApp] Loading data from: {data_path}")
        # For example:
        # if data_path.endswith('.mat'):
        #     ...
        # elif data_path.endswith('.h5'):
        #     ...
        # else:
        #     ...
        # Once loaded, you might update tabs or data states as needed.
        # For demonstration, we'll just print.

def main():
    app = QApplication(sys.argv)

    # Step 1: Launch the StartupDialog
    dialog = StartupDialog()
    dialog_result = dialog.exec()

    if dialog_result == QDialog.DialogCode.Accepted and dialog.selected_path:
        # Step 2: If user selected a dataset, launch the main GUI
        window = CaImagingApp(data_path=dialog.selected_path)
        window.show()
        sys.exit(app.exec())
    else:
        # If user cancels, exit the application
        sys.exit(0)

if __name__ == "__main__":
    main()