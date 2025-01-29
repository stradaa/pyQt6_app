"""
Generate a sample .h5 file containing multiple groups and datasets
for testing purposes.
"""

import numpy as np
import h5py

def create_sample_h5(filename: str = "sample.h5"):
    # Open a file in write mode (will overwrite if file exists).
    with h5py.File(filename, "w") as f:
        # ---------------------------
        # Create the first group.
        # ---------------------------
        group1 = f.create_group("Group1")

        # Create a random float32 dataset in Group1.
        data1 = np.random.rand(10, 10).astype(np.float32)
        dset1 = group1.create_dataset("Dataset1", data=data1)
        dset1.attrs["description"] = "Random 10x10 float32 array"

        # Create another dataset in Group1 with random integers.
        data2 = np.random.randint(0, 100, size=(5, 7)).astype(np.int32)
        dset2 = group1.create_dataset("Dataset2", data=data2)
        dset2.attrs["description"] = "Random 5x7 int32 array"

        # Create a small string dataset in Group1 for demonstration.
        str_data = np.array([b"Hello", b"World", b"PyQt6", b"h5py"], dtype="S10")
        dset3 = group1.create_dataset("StringDataset", data=str_data)
        dset3.attrs["description"] = "Array of short strings"

        # ---------------------------
        # Create the second group.
        # ---------------------------
        group2 = f.create_group("Group2")

        # Create a 1D dataset in Group2.
        data4 = np.linspace(0, 1, num=100).astype(np.float64)
        dset4 = group2.create_dataset("Linspace", data=data4)
        dset4.attrs["description"] = "Linspace from 0 to 1 with 100 points"

        # Create a second dataset in Group2 with a different shape.
        data5 = np.random.randn(20, 3).astype(np.float64)
        dset5 = group2.create_dataset("RandomNormal", data=data5)
        dset5.attrs["description"] = "20x3 float64 array from normal distribution"

        # ---------------------------
        # Create a dataset at the root level (no group).
        # ---------------------------
        root_data = np.array([[1, 2, 3, 4],
                              [5, 6, 7, 8],
                              [9, 10, 11, 12]], dtype=np.int32)
        dset_root = f.create_dataset("RootDataset", data=root_data)
        dset_root.attrs["description"] = "3x4 int32 array at root level"

    print(f"Sample HDF5 file '{filename}' created successfully.")

if __name__ == "__main__":
    create_sample_h5("sample.h5")
