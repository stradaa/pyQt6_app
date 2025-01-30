import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog
)
from PyQt6.QtGui import QAction

# dependencies
from startup_dialog import StartupDialog
from main_window import GraFTMainWindow
from data_selection_dialog import DataSelectionDialog

###############################################################################
# The Application Controller
###############################################################################
class GraFT_App:
    """
    This class orchestrates the entire application:
    - Manages the QApplication instance
    - Shows the StartupDialog
    - On success, creates and shows the main window
    """

    def __init__(self):
        self.app = QApplication(sys.argv)   # The standard Qt Application
        self.main_window = None            # Will hold a reference to the main window

    # def run(self):
    #     # 1) Show the initial startup dialog
    #     startup_dialog = StartupDialog()
    #     if startup_dialog.exec() == QDialog.DialogCode.Accepted and startup_dialog.selected_path:

    #         # 2) Let the user select data from that path
    #         data_dialog = DataSelectionDialog(startup_dialog.selected_path)

    #         if data_dialog.exec() == QDialog.DialogCode.Accepted:
    #             # The user picked variables/items. Create the main window.
    #             self.main_window = GraFTMainWindow(
    #                 data_path=startup_dialog.selected_path,
    #                 selected_items=data_dialog.selected_items  # Optionally pass it in
    #             )
    #             self.main_window.show()

    #             # Start event loop
    #             sys.exit(self.app.exec())
    #         else:
    #             # The user canceled the data selection
    #             print("User canceled data selection. Exiting.")
    #             sys.exit(0)
    #     else:
    #         # The user canceled in the startup dialog
    #         print("User canceled startup. Exiting.")
    #         sys.exit(0)

    def run(self):
        """
        Runs the application by first showing StartupDialog.
        If the user cancels DataSelectionDialog, they are returned to StartupDialog.
        """
        while True:  # Keep showing StartupDialog until a dataset is successfully selected
            startup_dialog = StartupDialog()
            if startup_dialog.exec() == QDialog.DialogCode.Accepted and startup_dialog.selected_path:
                
                # 2) Show DataSelectionDialog for selecting dataset
                data_dialog = DataSelectionDialog(startup_dialog.selected_path)
                if data_dialog.exec() == QDialog.DialogCode.Accepted:
                    
                    # The user successfully selected a dataset, start the main application
                    self.main_window = GraFTMainWindow(
                        data_path=startup_dialog.selected_path,
                        selected_items=data_dialog.selected_items
                    )
                    self.main_window.show()

                    # Start event loop and exit loop (successful launch)
                    sys.exit(self.app.exec())

                else:
                    # User canceled DataSelectionDialog → Go back to StartupDialog
                    print("[GraFT_App] User canceled DataSelectionDialog, returning to StartupDialog.")
                    continue  # Restart the loop

            else:
                # User canceled StartupDialog → Exit application
                print("[GraFT_App] User canceled StartupDialog. Exiting application.")
                sys.exit(0)
