import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QMainWindow, QWidget, QTabWidget, QMessageBox)
from PyQt6.QtGui import QAction

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
        # At this point, you already know which items user selected:
        if self.selected_items:
            print("Hello")
            print("[MainApp] The user selected:")
            for name, dtype in self.selected_items:
                print(dir(self.selected_items))
                print(f"  - {name} ({dtype})")
        else:
            print("Here -alex")
            print("[MainApp] No items were selected.")


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
        Launch a new StartupDialog to pick a folder or file,
        then open a NEW main window for that dataset.
        """
        dialog = StartupDialog(self)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted and dialog.selected_path:
            # 2) Now show the DataSelectionDialog to pick which items to load
            data_dialog = DataSelectionDialog(dialog.selected_path, parent=self)
            data_result = data_dialog.exec()

            if data_result == QDialog.DialogCode.Accepted:
                # The user selected items to load
                selected_items = data_dialog.selected_items

                # 3) Create the new main window, pass both the data path and the item selections
                new_window = GraFTMainWindow(
                    data_path=dialog.selected_path,
                    selected_items=selected_items
                )
                new_window.show()

                # Keep a reference so the new window isn't garbage-collected
                if not hasattr(self, '_open_projects'):
                    self._open_projects = []
                self._open_projects.append(new_window)

            else:
                # The user canceled the DataSelectionDialog
                print("[MainWindow] User canceled data selection in open_dataset()")
