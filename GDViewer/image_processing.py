import imagej
from scyjava import jimport

def convert_to_imagej_dataset(ij, data):
    return ij.py.to_dataset(data)

def show_slice(ij, data_slice, title):
    img = convert_to_imagej_dataset(ij, data_slice)
    ij.ui().show(title, img, cmap='gray')
    img = ij.py.active_imageplus()
    return img

def update_slice(ij, data_slice, title, img):
    data_java = ij.py.to_java(data_slice)
    ImagePlus = jimport('ij.ImagePlus')
    img2 = ij.convert().convert(data_java, ImagePlus)
    img.setImage(img2)
    img.setTitle(title)
    return img

