import zarr
import time
from colorama import Fore

def find_resolutions(store):
    metadata = store.attrs.asdict()
    multiscales = metadata.get('multiscales', [])
    if not multiscales:
        raise ValueError("No multiscales information found in the metadata.")
    datasets = multiscales[0].get('datasets', [])
    resolutions = [dataset['path'] for dataset in datasets]
    return resolutions

def load_slice(store, resolution_level, axis, index):
    if resolution_level in store:
        start_time = time.time()
        if axis == 0:
            data_slice = store[resolution_level][index, :, :]
        elif axis == 1:
            data_slice = store[resolution_level][:, index, :]
        elif axis == 2:
            data_slice = store[resolution_level][:, :, index]
        else:
            raise ValueError("Invalid axis value. Must be 0, 1, or 2.")
        end_time = time.time()
        print(Fore.GREEN + f"Loaded slice at index {index} along axis {axis} from resolution {resolution_level} in {end_time - start_time:.2f} seconds")
        return data_slice
    else:
        raise ValueError(f"Resolution level {resolution_level} not found in the ZARR store.")

def validate_slice(data_slice):
    if data_slice.ndim != 2:
        raise ValueError("Loaded slice is not a 2D array")
    return data_slice

def get_volume_size(store, resolution_level):
    if resolution_level in store:
        shape = store[resolution_level].shape
        return shape
    else:
        raise ValueError(f"Resolution level {resolution_level} not found in the ZARR store.")

