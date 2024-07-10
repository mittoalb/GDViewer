import tkinter as tk
import zarr
from tkinter import ttk
from concurrent.futures import ThreadPoolExecutor
from GDViewer.utils import find_resolutions, load_slice, validate_slice, get_volume_size, open_zarr_store
from GDViewer.image_processing import show_slice, update_slice
from GDViewer.log import info, error, warning, setup_custom_logger

axial_img = None
sagittal_img = None
coronal_img = None
current_store = None
current_resolution = None
current_indices = {'axial': None, 'sagittal': None, 'coronal': None}

def show_dialog(ij):
    global axial_img, sagittal_img, coronal_img, current_store, current_resolution, current_indices

    def update_action():
        global axial_img, sagittal_img, coronal_img, current_store, current_resolution, current_indices

        zarr_url = str(url_field.get())
        token = str(token_field.get())  # Get the token from the input field
        resolution_layer = resolution_slider.get()  # Ensure resolution_layer is assigned here
        axial_index = axial_slider.get()
        sagittal_index = sagittal_slider.get()
        coronal_index = coronal_slider.get()

        info(f"Opening ZARR store from {zarr_url} with resolution layer {resolution_layer}...")  # Log message

        try:
            store = open_zarr_store(zarr_url, token)  # Open the ZARR store with or without the token
            current_store = store
            info(f"Zarr store opened: {store}")  # Log message
            display_title = zarr_url.split('/')[-1]
            resolutions = find_resolutions(store)
            info(f"Resolutions layers: {resolutions}")  # Log message

            if current_resolution != resolutions[resolution_layer]:
                current_resolution = resolutions[resolution_layer]
                info(f"Current resolution layer: {current_resolution}")  # Log message
                current_indices = {'axial': None, 'sagittal': None, 'coronal': None}  # Reset indices on resolution change

            volume_size = get_volume_size(store, current_resolution)
            info(f"Volume size at resolution '{current_resolution}': {volume_size}")  # Log message

            if not (0 <= axial_index < volume_size[0]):
                error(f"Axial index {axial_index} out of range. Valid range is 0 to {volume_size[0] - 1}")  # Log error
                return
            if not (0 <= sagittal_index < volume_size[1]):
                error(f"Sagittal index {sagittal_index} out of range. Valid range is 0 to {volume_size[1] - 1}")  # Log error
                return
            if not (0 <= coronal_index < volume_size[2]):
                error(f"Coronal index {coronal_index} out of range. Valid range is 0 to {volume_size[2] - 1}")  # Log error
                return

            info(f"Valid axial index range: 0 to {volume_size[0] - 1}")  # Log message
            info(f"Valid sagittal index range: 0 to {volume_size[1] - 1}")  # Log message
            info(f"Valid coronal index range: 0 to {volume_size[2] - 1}")  # Log message

            with ThreadPoolExecutor() as executor:
                futures = {}
                if current_indices['axial'] != axial_index:
                    futures['axial'] = executor.submit(load_slice, store, current_resolution, 0, axial_index)
                if current_indices['sagittal'] != sagittal_index:
                    futures['sagittal'] = executor.submit(load_slice, store, current_resolution, 1, sagittal_index)
                if current_indices['coronal'] != coronal_index:
                    futures['coronal'] = executor.submit(load_slice, store, current_resolution, 2, coronal_index)

                results = {key: future.result() for key, future in futures.items()}

            if 'axial' in results:
                axial_slice = validate_slice(results['axial'])
                if axial_img is not None:
                    axial_img = update_slice(ij, axial_slice, f"Axial Slice {axial_index} {display_title}", axial_img)
                else:
                    axial_img = show_slice(ij, axial_slice, f"Axial Slice {axial_index} {display_title}")
                current_indices['axial'] = axial_index

            if 'sagittal' in results:
                sagittal_slice = validate_slice(results['sagittal'])
                if sagittal_img is not None:
                    sagittal_img = update_slice(ij, sagittal_slice, f"Sagittal Slice {sagittal_index} {display_title}", sagittal_img)
                else:
                    sagittal_img = show_slice(ij, sagittal_slice, f"Sagittal Slice {sagittal_index} {display_title}")
                current_indices['sagittal'] = sagittal_index

            if 'coronal' in results:
                coronal_slice = validate_slice(results['coronal'])
                if coronal_img is not None:
                    coronal_img = update_slice(ij, coronal_slice, f"Coronal Slice {coronal_index} {display_title}", coronal_img)
                else:
                    coronal_img = show_slice(ij, coronal_slice, f"Coronal Slice {coronal_index} {display_title}")
                current_indices['coronal'] = coronal_index

            info("Slices displayed")  # Log message

        except Exception as e:
            error(f"Error: {e}")  # Log error

    root = tk.Tk()
    root.title("Globus Data Viewer")
    root.geometry("900x350")

    tk.Label(root, text="DATA URL:").place(x=20, y=20)
    url_field = tk.Entry(root, width=50)
    url_field.place(x=120, y=20)
    url_field.insert(0, "https://g-df2e9.fd635.8443.data.globus.org/ESRF_APRIL_ZARR/Brain_715699L_0.854um.zarr")

    tk.Label(root, text="Token:").place(x=20, y=60)
    token_field = tk.Entry(root, width=50)
    token_field.place(x=120, y=60)

    tk.Label(root, text="Resolution Layer:").place(x=20, y=100)
    resolution_slider = tk.Scale(root, from_=0, to=6, orient=tk.HORIZONTAL)
    resolution_slider.place(x=240, y=100)

    tk.Label(root, text="Axial Slice Index:").place(x=20, y=160)
    axial_slider = tk.Scale(root, from_=0, to=1000, orient=tk.HORIZONTAL)
    axial_slider.place(x=240, y=160)

    tk.Label(root, text="Sagittal Slice Index:").place(x=20, y=220)
    sagittal_slider = tk.Scale(root, from_=0, to=1000, orient=tk.HORIZONTAL)
    sagittal_slider.place(x=240, y=220)

    tk.Label(root, text="Coronal Slice Index:").place(x=20, y=280)
    coronal_slider = tk.Scale(root, from_=0, to=1000, orient=tk.HORIZONTAL)
    coronal_slider.place(x=240, y=280)

    update_button = tk.Button(root, text="Update", command=update_action)
    update_button.place(x=700, y=100)

    root.mainloop()

