import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QMainWindow, QWidget, QTabWidget, QMessageBox)
from PyQt6.QtGui import QAction
import h5py
import scipy
from pynwb import NWBHDF5IO
import numpy as np

# dependencies
from tabs_preprocessing import (PreprocessingTab, ParameterSetupTab, 
    AlgorithmExecutionTab, ResultsVisualizationTab
)
from startup_dialog import StartupDialog

import os
from data_selection_dialog import DataSelectionDialog

###############################################################################
# The Main Window
###############################################################################
class GraFTMainWindow(QMainWindow):
    """
    Main Application Window.
    Initialized with a data_path from the StartupDialog.
    """
    def __init__(self, data_path=None, selected_items=None, parent=None):
        super().__init__(parent)

        self.data_path = data_path
        self.selected_items = selected_items  # from the DataSelectionDialog

        self.setWindowTitle("GraFT-App")
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
            self.load_data()

    def _get_modern_style(self):
        """
        Returns a stylesheet string. 
        Keep this separate for easier modification or theming.
        """
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
    

    def load_data(self):
        print(f"[MainApp] Loading data from: {self.data_path}")

        self.loaded_data = {}  # Dictionary to store the loaded data

        # At this point, you already know which items user selected:
        if self.selected_items:
            print("[MainApp] The user selected:")
            print("Total Selected: ", len(self.selected_items))
            for name, dtype in self.selected_items:
                print(f"  - {name} ({dtype})")
        else:
            print("[MainApp] No items were selected.")
            return
        
        # Load data based on the file type
        if self.data_path.lower().endswith(('.h5', '.hdf5')):
            self._load_hdf5_data()
        elif self.data_path.lower().endswith('.mat'):
            self._load_mat_data()
        elif self.data_path.lower().endswith('.nwb'):
            self._load_nwb_data()
        else:
            print("[MainApp] Unsupported file type.")

        # At this point, self.loaded_data contains the loaded datasets
        if self.loaded_data:
            print("[MainApp] Data successfully loaded:")
            for name in self.loaded_data.keys():
                print(f"  - {name}: {self.loaded_data[name].shape} (shape)")
        else:
            print("[MainApp] No data was loaded.")


    # def _load_hdf5_data(self):
    #     """
    #     Load selected datasets from an HDF5 file.
    #     """
    #     try:
    #         with h5py.File(self.data_path, 'r') as f:
    #             for name, dtype in self.selected_items:
    #                 if dtype == "Dataset":
    #                     self.loaded_data[name] = np.array(f[name])  # Convert to a NumPy array
    #                     print(f"[MainApp] Loaded dataset '{name}' from HDF5 file.")
    #                 else:
    #                     print(f"[MainApp] Skipping '{name}', as it is not a dataset.")
    #     except Exception as e:
    #         print(f"[MainApp] Error loading HDF5 file: {e}")

    def _load_hdf5_data(self):
        """
        Load selected datasets from an HDF5 (.h5 or .hdf5) file and print the results.
        Supports nested groups within the HDF5 file.
        """
        try:
            with h5py.File(self.data_path, 'r') as f:
                for full_path, dtype in self.selected_items:
                    # Convert Windows-style backslashes to forward slashes for HDF5 paths
                    dataset_path = full_path.replace("\\", "/")

                    # Extract the relative dataset path inside the HDF5 file
                    relative_path = dataset_path.replace(self.data_path.replace("\\", "/"), "").lstrip("/")

                    if relative_path in f:
                        data = np.array(f[relative_path])  # Convert dataset to NumPy array
                        self.loaded_data[relative_path] = data
                        print(f"\n[MainApp] Successfully loaded dataset '{relative_path}':\n", data)

                    else:
                        print(f"[MainApp] Dataset '{relative_path}' not found in HDF5 file.")

        except Exception as e:
            print(f"[MainApp] Error loading HDF5 file: {e}")


    def _load_mat_data(self):
        """
        Load selected variables from a MATLAB .mat file and print the result.
        """
        def is_mat73(file_path):
            """
            Returns True if file_path is a MATLAB v7.3 file (i.e., an HDF5 file),
            False otherwise.
            """
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(128)
                return b'MATLAB 7.3 MAT-file' in header
            except Exception:
                return False

        if is_mat73(self.data_path):
            # If it's a MATLAB v7.3 file, treat it like an HDF5 file
            self._load_hdf5_data()
            return

        try:
            # Load the .mat file
            mat_dict = scipy.io.loadmat(self.data_path, squeeze_me=False, struct_as_record=False)

            for full_path, dtype in self.selected_items:
                var_name = os.path.basename(full_path)  # Extract just the variable name

                if var_name in mat_dict:
                    data = mat_dict[var_name]  # Extract data

                    # Convert MATLAB struct objects to dictionary for readability
                    if isinstance(data, np.ndarray) and data.dtype.names is not None:
                        data = {field: data[field] for field in data.dtype.names}

                    self.loaded_data[var_name] = data  # Store loaded variable
                    print(f"\n[MainApp] Successfully loaded variable '{var_name}':\n", data) # print for now

                else:
                    print(f"[MainApp] '{var_name}' not found in .mat file.")

        except Exception as e:
            print(f"[MainApp] Error loading .mat file: {e}")


    def _load_nwb_data(self):
        """
        Load selected datasets from an NWB file.
        """
        try:
            with NWBHDF5IO(self.data_path, 'r') as io:
                nwbfile = io.read()

                for name, dtype in self.selected_items:
                    try:
                        # Check if dataset exists in NWB file
                        if hasattr(nwbfile, name):
                            dataset = getattr(nwbfile, name)
                            self.loaded_data[name] = np.array(dataset.data[:])  # Convert to NumPy array
                            print(f"[MainApp] Loaded dataset '{name}' from NWB file.")
                        else:
                            print(f"[MainApp] '{name}' not found in NWB file.")
                    except Exception as e:
                        print(f"[MainApp] Error extracting '{name}' from NWB: {e}")

        except Exception as e:
            print(f"[MainApp] Error loading NWB file: {e}")


    def _create_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        open_action = QAction("Open Another Dataset", self)
        open_action.triggered.connect(self.open_dataset)
        file_menu.addAction(open_action)

        # View menu
        view_menu = menubar.addMenu("View")
        view_action = QAction("Appearance", self)
        view_menu.addAction(view_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        # Go menu
        run_menu = menubar.addMenu("Run")

        # Help menu
        help_menu = menubar.addMenu("Help")


    def open_dataset(self):
        """
        Launches StartupDialog to pick a file or folder.
        If user cancels, return to StartupDialog.
        """
        while True:  # Keep showing StartupDialog until a valid selection is made
            dialog = StartupDialog(self)
            result = dialog.exec()

            if result == QDialog.DialogCode.Accepted and dialog.selected_path:
                data_path = dialog.selected_path

                # Show DataSelectionDialog to pick which dataset to load
                data_dialog = DataSelectionDialog(data_path, parent=self)
                data_result = data_dialog.exec()

                if data_result == QDialog.DialogCode.Accepted:
                    # The user selected a dataset
                    selected_items = data_dialog.selected_items

                    # Open the main application window with the selected dataset
                    new_window = GraFTMainWindow(data_path=data_path, selected_items=selected_items)
                    new_window.show()

                    # Store reference so it's not garbage collected
                    if not hasattr(self, '_open_projects'):
                        self._open_projects = []
                    self._open_projects.append(new_window)
                    
                    break  # Exit the loop since a dataset is selected

                else:
                    print("[MainWindow] User canceled DataSelectionDialog, returning to StartupDialog.")
                    continue  # Restart the loop to show StartupDialog again

            else:
                print("[MainWindow] User canceled StartupDialog, closing application.")
                break  # Exit loop if user cancels StartupDialog
