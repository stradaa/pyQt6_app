import os
import h5py
import scipy.io
from PyQt6.QtWidgets import (
    QDialog,
    QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt

class DataSelectionDialog(QDialog):
    """
    Dialog that lets a user see what is inside a folder or file,
    and select certain items to load.
    """
    def __init__(self, data_path, parent=None):
        super().__init__(parent)
        self.data_path = data_path
        self.selected_items = []
        self.setWindowTitle("Select Data to Load")

        # Main layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.info_label = QLabel(f"Preview: {self.data_path}")
        self.layout.addWidget(self.info_label)

        # Tree widget to display contents
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Name", "Type"])
        self.layout.addWidget(self.tree_widget)

        # Button layout
        btn_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        btn_layout.addWidget(self.ok_button)
        btn_layout.addWidget(self.cancel_button)

        # Connect signals
        self.ok_button.clicked.connect(self.on_ok)
        self.cancel_button.clicked.connect(self.reject)

        self.layout.addLayout(btn_layout)

        # Load the path structure
        self.populate_tree()

    def populate_tree(self):
        """
        Depending on whether data_path is a folder or a file (and which file type),
        build a tree to show user what is inside.
        """
        if os.path.isdir(self.data_path):
            self._populate_tree_with_folder(self.data_path)
        else:
            _, ext = os.path.splitext(self.data_path)
            ext = ext.lower()
            if ext in [".mat", ".m"]:
                self._populate_tree_with_mat(self.data_path)
            elif ext in [".h5", ".hdf5"]:
                self._populate_tree_with_hdf5(self.data_path)
            else:
                # Fallback for unsupported file type
                item = QTreeWidgetItem(["(No structured preview)", "Unknown"])
                self.tree_widget.addTopLevelItem(item)


    def _populate_tree_with_folder(self, folder_path):
        """
        List all files in the folder (non-recursive for simplicity).
        """
        try:
            files = os.listdir(folder_path)
            files.sort()
            for f in files:
                full_path = os.path.join(folder_path, f)
                item_type = "Folder" if os.path.isdir(full_path) else "File"
                top_item = QTreeWidgetItem([f, item_type])
                top_item.setCheckState(0, Qt.CheckState.Unchecked)
                self.tree_widget.addTopLevelItem(top_item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load folder: {e}")


    def _populate_tree_with_mat(self, mat_path):
        """
        Use scipy.io.loadmat for older .mat files. 
        If it's actually v7.3, treat it like HDF5.
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

        if is_mat73(mat_path):
            # It's really an HDF5 in disguise. Use our HDF5 routine instead.
            self._populate_tree_with_hdf5(mat_path)
            return

        # Otherwise, try the normal loadmat approach:
        try:
            import scipy.io
            mat_dict = scipy.io.loadmat(mat_path, squeeze_me=False, struct_as_record=False)
            # Filter out the special keys like '__header__', etc.
            for k in mat_dict:
                if k.startswith("__"):
                    continue
                dtype_str = str(type(mat_dict[k]))
                item = QTreeWidgetItem([k, dtype_str])
                item.setCheckState(0, Qt.CheckState.Unchecked)
                self.tree_widget.addTopLevelItem(item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load .mat file:\n{e}")


    # def _populate_tree_with_hdf5(self, h5_path):
    #     try:
    #         import h5py
    #         with h5py.File(h5_path, 'r') as f:
    #             for key in f.keys():
    #                 obj = f[key]
    #                 if isinstance(obj, h5py.Group):
    #                     item_type = "Group"
    #                 elif isinstance(obj, h5py.Dataset):
    #                     item_type = "Dataset"
    #                 else:
    #                     item_type = "Unknown"

    #                 item = QTreeWidgetItem([key, item_type])
    #                 item.setCheckState(0, Qt.CheckState.Unchecked)
    #                 self.tree_widget.addTopLevelItem(item)
    #     except Exception as e:
    #         QMessageBox.warning(self, "Error", f"Failed to load HDF5 file: {e}")

    def _populate_tree_with_hdf5(self, h5_path):
        """
        Recursively populates the tree with the structure of an HDF5 file.
        """
        try:
            import h5py
            with h5py.File(h5_path, 'r') as f:
                self._add_hdf5_items(f, self.tree_widget.invisibleRootItem())

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load HDF5 file: {e}")

    def _add_hdf5_items(self, h5_group, parent_item):
        """
        Recursively adds items from an HDF5 group to the tree.
        
        Parameters:
        - h5_group: The current HDF5 group (or file) being explored.
        - parent_item: The parent QTreeWidgetItem to which new items are added.
        """
        for key in h5_group.keys():
            obj = h5_group[key]
            
            if isinstance(obj, h5py.Group):  # If it's a group, recurse into it
                item = QTreeWidgetItem([key, "Group"])
                parent_item.addChild(item)
                self._add_hdf5_items(obj, item)  # Recursively add items inside this group

            elif isinstance(obj, h5py.Dataset):  # If it's a dataset, add as a selectable item
                item = QTreeWidgetItem([key, "Dataset"])
                item.setCheckState(0, Qt.CheckState.Unchecked)
                parent_item.addChild(item)


    def on_ok(self):
        """
        Gather which items are checked, then accept the dialog.
        """
        self.selected_items = []
        root = self.tree_widget.invisibleRootItem()
        for i in range(root.childCount()):
            child = root.child(i)
            if child.checkState(0) == Qt.CheckState.Checked:
                name = child.text(0)
                data_type = child.text(1)
                self.selected_items.append((name, data_type))

        self.accept()