import imagej
import scyjava as sj
import signal
import sys
import time
import os
import click
from threading import Event
from GDViewer.gui import show_dialog
from GDViewer.log import setup_custom_logger, info

# Initialize the custom logger
setup_custom_logger(stream_to_console=True)

# Initialize global variables
axial_img = None
sagittal_img = None
coronal_img = None
stop_event = Event()
current_store = None
current_resolution = None
current_indices = {'axial': None, 'sagittal': None, 'coronal': None}

def signal_handler(sig, frame):
    global stop_event
    info('Exiting gracefully...')
    stop_event.set()
    ij.context().dispose()
    sys.exit(0)

def initialize_imagej(imagej_path='sc.fiji:fiji', mode='interactive'):
    """
    Initializes ImageJ with the specified mode and version.

    Parameters:
    imagej_path (str): The path or version of ImageJ to initialize.
    mode (str): The mode to run ImageJ ('interactive' or 'headless').

    Returns:
    ImageJ instance or None if initialization fails.
    """
    try:
        # Check if the provided path exists
        if os.path.exists(imagej_path):
            print(f"Using ImageJ installation at: {imagej_path}")
            ij = imagej.init(imagej_path, mode=mode)
        else:
            print(f"Provided path does not exist. Using default ImageJ version: {imagej_path}")
            ij = imagej.init(imagej_path, mode=mode)
        
        # Verify the initialization
        if ij is None:
            raise RuntimeError("ImageJ initialization returned None")
        
        print("ImageJ initialized successfully")
        return ij
    except Exception as e:
        print(f"Error initializing ImageJ: {e}")
        return None

@click.command()
@click.option('--imagej-path', default='sc.fiji:fiji', help='Path to ImageJ installation')
def main(imagej_path):
    global ij
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("Initializing ImageJ...")
    ij = initialize_imagej(imagej_path, mode='interactive')
    if ij is None:
        print("Failed to initialize ImageJ. Exiting.")
        return

    ij.ui().showUI()
    sj.jimport('ij.ImagePlus')
    time.sleep(2)  # Give time for the UI to initialize

    info("ImageJ initialized.")

    show_dialog(ij)

    while not stop_event.is_set():
        time.sleep(1)

if __name__ == "__main__":
    main()

