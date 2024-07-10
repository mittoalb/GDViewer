import tkinter as tk
from tkinter import ttk
from colorama import Fore
from concurrent.futures import ThreadPoolExecutor
from GDViewer.utils import find_resolutions, load_slice, validate_slice, get_volume_size
from GDViewer.image_processing import show_slice, update_slice
import zarr

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
        print(zarr_url)
        resolution_layer = resolution_slider.get()
        axial_index = axial_slider.get()
        sagittal_index = sagittal_slider.get()
        coronal_index = coronal_slider.get()

        print(Fore.CYAN + f"Opening ZARR store from {zarr_url} with resolution layer {resolution_layer}...")
        try:
            store = zarr.open_group(zarr_url, mode='r')
            current_store = store
            print(Fore.GREEN + "Zarr store opened:", store)
            display_title = zarr_url.split('/')[-1]
            resolutions = find_resolutions(store)
            print(Fore.CYAN + f"Resolutions layers: {resolutions}")

            if current_resolution != resolutions[resolution_layer]:
                current_resolution = resolutions[resolution_layer]
                print(Fore.CYAN + f"Current resolution layer: {current_resolution}")
                current_indices = {'axial': None, 'sagittal': None, 'coronal': None}  # Reset indices on resolution change

            volume_size = get_volume_size(store, current_resolution)
            print(Fore.CYAN + f"Volume size at resolution '{current_resolution}': {volume_size}")

            if not (0 <= axial_index < volume_size[0]):
                print(Fore.RED + f"Axial index {axial_index} out of range. Valid range is 0 to {volume_size[0] - 1}")
                return
            if not (0 <= sagittal_index < volume_size[1]):
                print(Fore.RED + f"Sagittal index {sagittal_index} out of range. Valid range is 0 to {volume_size[1] - 1}")
                return
            if not (0 <= coronal_index < volume_size[2]):
                print(Fore.RED + f"Coronal index {coronal_index} out of range. Valid range is 0 to {volume_size[2] - 1}")
                return

            print(Fore.GREEN + f"Valid axial index range: 0 to {volume_size[0] - 1}")
            print(Fore.GREEN + f"Valid sagittal index range: 0 to {volume_size[1] - 1}")
            print(Fore.GREEN + f"Valid coronal index range: 0 to {volume_size[2] - 1}")

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

            print(Fore.GREEN + "Slices displayed")

        except Exception as e:
            print(Fore.RED + f"Error: {e}")

    root = tk.Tk()
    root.title("ZARR Viewer Settings")
    root.geometry("500x400")

    tk.Label(root, text="ZARR URL:").place(x=20, y=20)
    url_field = tk.Entry(root, width=50)
    url_field.place(x=120, y=20)
    url_field.insert(0, "https://g-df2e9.fd635.8443.data.globus.org/ESRF_APRIL_ZARR/Brain_715699L_0.854um.zarr")

    tk.Label(root, text="Resolution Layer:").place(x=20, y=60)
    resolution_slider = tk.Scale(root, from_=0, to=10, orient=tk.HORIZONTAL)
    resolution_slider.place(x=140, y=60)

    tk.Label(root, text="Axial Slice Index:").place(x=20, y=120)
    axial_slider = tk.Scale(root, from_=0, to=1000, orient=tk.HORIZONTAL)
    axial_slider.place(x=140, y=120)

    tk.Label(root, text="Sagittal Slice Index:").place(x=20, y=180)
    sagittal_slider = tk.Scale(root, from_=0, to=1000, orient=tk.HORIZONTAL)
    sagittal_slider.place(x=140, y=180)

    tk.Label(root, text="Coronal Slice Index:").place(x=20, y=240)
    coronal_slider = tk.Scale(root, from_=0, to=1000, orient=tk.HORIZONTAL)
    coronal_slider.place(x=140, y=240)

    update_button = tk.Button(root, text="Update", command=update_action)
    update_button.place(x=200, y=300)

    root.mainloop()

