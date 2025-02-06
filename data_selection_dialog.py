import os
import h5py
from PyQt6.QtWidgets import (
    QDialog,
    QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt
from pynwb import NWBHDF5IO


class DataSelectionDialog(QDialog):
    """
    Dialog that lets a user see what is inside a folder or file,
    and select certain items to load.
    """
    def __init__(self, data_path, parent=None):
        super().__init__(parent)
        self.data_path = data_path
        self.selected_items = []
        self.select_type = ''   # 'Folder' or 'File'
        self.setWindowTitle("Select Data to Load")

        # Main layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.info_label = QLabel(f"Preview: {self.data_path}")
        self.layout.addWidget(self.info_label)

        # Checkbox for selecting all images in folder
        self.select_all_images_checkbox = QCheckBox("Select all images in folder")
        self.select_all_images_checkbox.stateChanged.connect(self.toggle_all_images_selection)
        self.layout.addWidget(self.select_all_images_checkbox)

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
            self.select_type = 'Folder'
        else:
            _, ext = os.path.splitext(self.data_path)
            ext = ext.lower()
            if ext == ".mat":
                self._populate_tree_with_mat(self.data_path)
            elif ext in [".h5", ".hdf5"]:
                self._populate_tree_with_hdf5(self.data_path)
            elif ext == ".nwb":
                self._populate_tree_with_nwb(self.data_path)  # NEW FUNCTION
            else:
                # Fallback for unsupported file type
                item = QTreeWidgetItem(["(No structured preview)", "Unknown"])
                self.tree_widget.addTopLevelItem(item)

            # remove the checkbox
            self.select_all_images_checkbox.setEnabled(False)  # Disable if <= file was selected
            self.select_all_images_checkbox.setVisible(False)  # Hide it

            self.select_type = 'File'


    def _populate_tree_with_folder(self, folder_path):
        """
        Populate the tree widget with image files in the selected folder.
        Enables the 'Select all images in folder' checkbox only if more than one image is found.
        """
        image_extensions = {".tiff", ".tif", ".png", ".jpg", ".jpeg", ".bmp"}

        try:
            self.tree_widget.clear()  # Clear any existing items in the tree
            files = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in image_extensions]
            files.sort()

            if len(files) > 1:
                self.select_all_images_checkbox.setEnabled(True)  # Enable checkbox
                self.select_all_images_checkbox.setVisible(True)  # Ensure it's visible
            else:
                self.select_all_images_checkbox.setEnabled(False)  # Disable if <= 1 file
                self.select_all_images_checkbox.setVisible(False)  # Hide it

            for f in files:
                full_path = os.path.join(folder_path, f)
                ext = os.path.splitext(f)[1].lower()
                size_bytes = os.path.getsize(full_path)
                size_mb = f"{size_bytes / (1024 ** 2):.2f} MB"

                top_item = QTreeWidgetItem([f, "Image Type", "", ext, size_mb])
                top_item.setCheckState(0, Qt.CheckState.Unchecked)

                self.tree_widget.addTopLevelItem(top_item)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load folder: {e}")


    def toggle_all_images_selection(self):
        """
        Check or uncheck all image files in the folder.
        """
        root = self.tree_widget.invisibleRootItem()
        check_state = (Qt.CheckState.Checked if self.select_all_images_checkbox.isChecked()
                       else Qt.CheckState.Unchecked)

        for i in range(root.childCount()):
            item = root.child(i)
            if item.text(1) == "Image Type":
                item.setCheckState(0, check_state)


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


    def _populate_tree_with_nwb(self, nwb_path):
        """
        Populates the tree with NWB file contents.
        """
        try:
            with NWBHDF5IO(nwb_path, 'r') as io:
                nwbfile = io.read()

                # Create a top-level NWB item
                nwb_item = QTreeWidgetItem(["NWB File", "Root", "", "", ""])
                self.tree_widget.addTopLevelItem(nwb_item)

                # Acquisition Data
                if nwbfile.acquisition:
                    acquisition_item = QTreeWidgetItem(["Acquisition", "Group", "", "", ""])
                    nwb_item.addChild(acquisition_item)
                    for name, dataset in nwbfile.acquisition.items():
                        self._add_nwb_dataset(acquisition_item, name, dataset)

                # Processing Modules
                if nwbfile.processing:
                    processing_item = QTreeWidgetItem(["Processing", "Group", "", "", ""])
                    nwb_item.addChild(processing_item)
                    for module_name, module in nwbfile.processing.items():
                        module_item = QTreeWidgetItem([module_name, "Module", "", "", ""])
                        processing_item.addChild(module_item)
                        for name, dataset in module.data_interfaces.items():
                            self._add_nwb_dataset(module_item, name, dataset)

                # Stimulus Data
                if nwbfile.stimulus:
                    stimulus_item = QTreeWidgetItem(["Stimulus", "Group", "", "", ""])
                    nwb_item.addChild(stimulus_item)
                    for name, dataset in nwbfile.stimulus.items():
                        self._add_nwb_dataset(stimulus_item, name, dataset)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load NWB file: {e}")


    def _add_nwb_dataset(self, parent_item, name, dataset):
        """
        Adds a dataset from NWB to the tree widget.
        """
        try:
            shape = str(dataset.data.shape) if hasattr(dataset, 'data') else "Unknown"
            dtype = str(dataset.data.dtype) if hasattr(dataset, 'data') else "Unknown"
            size_bytes = dataset.data.nbytes if hasattr(dataset, 'data') else 0
            size_mb = f"{size_bytes / (1024 ** 2):.2f}"  # Convert to MB

            item = QTreeWidgetItem([name, "Dataset", shape, dtype, size_mb])
            item.setCheckState(0, Qt.CheckState.Unchecked)
            parent_item.addChild(item)
        except Exception as e:
            print(f"[DataSelectionDialog] Error adding NWB dataset '{name}': {e}")


    def limit_dataset_selection(self, item, column):
        """
        Ensures that only one dataset can be selected at a time.
        If a new dataset is checked, all other datasets are unchecked.
        """
        if item.checkState(0) == Qt.CheckState.Checked and item.text(1) != "Image Type":
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
        Ensures selected dataset(s) are passed to self.selected_items.
        - If a file was selected, only one dataset is stored.
        - If a folder was selected, all checked images in the folder are stored.
        """
        self.selected_items = []
        root = self.tree_widget.invisibleRootItem()

        def find_selected_items(item, parent_path=""):
            """
            Recursively finds selected datasets or image files.
            """
            name = item.text(0)
            data_type = item.text(1)
            full_path = os.path.join(parent_path, name).strip("/")

            # Handling case where a FILE is selected (preserving original logic)
            if self.select_type == 'File':
                if item.childCount() == 0 and item.checkState(0) == Qt.CheckState.Checked and \
                        (data_type == "Dataset" or data_type == "Image Type"):
                    self.selected_items = [(full_path, data_type)]  # Store the single selected dataset
                    return

                for i in range(item.childCount()):
                    find_selected_items(item.child(i), full_path)

            # Handling case where a FOLDER is selected (NEW FUNCTIONALITY)
            elif self.select_type == 'Folder':
                if item.checkState(0) == Qt.CheckState.Checked and data_type == "Image Type":
                    self.selected_items.append((full_path, data_type))  # Store all selected images

                for i in range(item.childCount()):
                    find_selected_items(item.child(i), full_path)

        # Start searching from root
        for i in range(root.childCount()):
            find_selected_items(root.child(i), self.data_path)

        # Confirm selection
        if self.selected_items:
            print(f"[DataSelectionDialog] Selected items: {self.selected_items}")
            self.accept()
        else:
            QMessageBox.warning(self, "Selection Required", "Please select at least one dataset or image before proceeding.")

