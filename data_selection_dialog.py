import os
import h5py
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
        self.tree_widget.setHeaderLabels(["Name", "Type", "Shape", "Data Type", "Size (MB)"])
        self.layout.addWidget(self.tree_widget)

        # Button layout
        btn_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        btn_layout.addWidget(self.ok_button)
        btn_layout.addWidget(self.cancel_button)

        # Connect signals
        self.ok_button.clicked.connect(self.on_ok)
        self.cancel_button.clicked.connect(self.on_cancel)
        self.tree_widget.itemChanged.connect(self.limit_dataset_selection)

        self.layout.addLayout(btn_layout)

        # Load the path structure
        self.populate_tree()

    
    def on_cancel(self):
        """
        Handles the case where the user cancels the DataSelectionDialog.
        """
        print("[DataSelectionDialog] User canceled selection.")
        self.reject()  # Close this dialog and return control to parent
    

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
            if ext in [".mat"]:
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
                dtype = str(type(mat_dict[k])) # Dataset type
                shape = str(mat_dict[k].shape)  # Dataset shape
                size_bytes = mat_dict[k].nbytes  # Total bytes
                size_mb = f"{size_bytes / (1024 ** 2):.2f}"  # Convert to MB

                # adding to tree widget item
                item = QTreeWidgetItem([k, "Dataset", shape, dtype, size_mb])
                item.setCheckState(0, Qt.CheckState.Unchecked)
                self.tree_widget.addTopLevelItem(item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load .mat file:\n{e}")


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


    def _add_hdf5_items(self, h5_group, parent_item, parent_path=""):
        """
        Recursively adds items from an HDF5 group to the tree, including metadata.

        Parameters:
        - h5_group: The current HDF5 group (or file) being explored.
        - parent_item: The parent QTreeWidgetItem to which new items are added.
        - parent_path: The full path to the current dataset or group.
        """
        for key in h5_group.keys():
            obj = h5_group[key]
            full_path = f"{parent_path}/{key}".strip("/")  # Construct full dataset path

            if isinstance(obj, h5py.Group):  
                item = QTreeWidgetItem([key, "Group", "", "", ""])  # Groups have no shape or size
                parent_item.addChild(item)
                self._add_hdf5_items(obj, item, full_path)  # Recursively add children

            elif isinstance(obj, h5py.Dataset):  
                shape = str(obj.shape)  # Dataset shape
                dtype = str(obj.dtype)  # Data type
                size_bytes = obj.size * obj.dtype.itemsize  # Total bytes
                size_mb = f"{size_bytes / (1024 ** 2):.2f}"  # Convert to MB

                item = QTreeWidgetItem([key, "Dataset", shape, dtype, size_mb])
                item.setCheckState(0, Qt.CheckState.Unchecked)
                parent_item.addChild(item)          


    def limit_dataset_selection(self, item, column):
        """
        Ensures that only one dataset can be selected at a time.
        If a new dataset is checked, all other datasets are unchecked.
        """
        if item.checkState(0) == Qt.CheckState.Checked:
            # Traverse all items and uncheck any other selected dataset
            def uncheck_all_others(tree_item, exclude_item):
                for i in range(tree_item.childCount()):
                    child = tree_item.child(i)
                    if child is not exclude_item and child.checkState(0) == Qt.CheckState.Checked:
                        child.setCheckState(0, Qt.CheckState.Unchecked)
                    # Recursively check inside groups
                    uncheck_all_others(child, exclude_item)

            # Start checking from root
            root = self.tree_widget.invisibleRootItem()
            uncheck_all_others(root, item)


    def on_ok(self):
        """
        Ensures only one selected dataset is passed to self.selected_items.
        """
        self.selected_items = []
        root = self.tree_widget.invisibleRootItem()

        def find_selected_dataset(item, parent_path=""):
            """
            Recursively finds the single selected dataset.
            """
            # Check if data is in root (contains no child)
            if item.childCount() == 0 and item.checkState(0) == Qt.CheckState.Checked and item.text(1) == "Dataset":
                name = item.text(0)
                data_type = item.text(1)
                full_path = f"{parent_path}/{name}".strip("/")

                self.selected_items = [(full_path, data_type)]
                return

            # this is used if it contains children to see if any of those have been selected
            for i in range(item.childCount()):
                child = item.child(i)
                name = child.text(0)
                data_type = child.text(1)
                full_path = f"{parent_path}/{name}".strip("/")

                if child.checkState(0) == Qt.CheckState.Checked and data_type == "Dataset":
                    # shape = child.text(2)
                    # dtype = child.text(3)
                    # size_mb = child.text(4)

                    # Store the only selected dataset
                    self.selected_items = [(full_path, data_type)]
                    return  # Stop searching once one is found

                # Continue searching in groups
                find_selected_dataset(child, full_path)

        # Start searching from root
        for i in range(root.childCount()):
            find_selected_dataset(root.child(i))

        # Confirm selection
        if self.selected_items:
            print(f"[DataSelectionDialog] Selected dataset: {self.selected_items[0]}")
            self.accept()
        else:
            QMessageBox.warning(self, "Selection Required", "Please select one dataset before proceeding.")
