import imagej
import scyjava as sj
import signal
import sys
import time
from colorama import init, Fore
from threading import Event
from GDViewer.gui import show_dialog

# Initialize colorama for colored terminal output
init(autoreset=True)

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
    print(Fore.YELLOW + 'Exiting gracefully...')
    stop_event.set()
    ij.context().dispose()
    sys.exit(0)

def main():
    global ij
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(Fore.CYAN + "Initializing ImageJ...")
    ij = imagej.init('sc.fiji:fiji', mode='interactive')
    ij.ui().showUI()
    sj.jimport('ij.ImagePlus')
    time.sleep(2)  # Give time for the UI to initialize

    print(Fore.GREEN + "ImageJ initialized.")

    show_dialog(ij)

    while not stop_event.is_set():
        time.sleep(1)

if __name__ == "__main__":
    main()

