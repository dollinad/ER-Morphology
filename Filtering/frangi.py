from skimage.data import camera
from skimage.filters import frangi, hessian
from PIL import Image
from skimage import io
import tifffile 
import matplotlib.pyplot as plt

def example():
    # tif file is read using 'tifffile' plugin
    im = io.imread("data.tif", plugin='tifffile')
    
    fig, ax = plt.subplots(ncols=2)
    
    # Show 'before' image
    # Index position 9 is a random selection
    ax[0].imshow(im[9], cmap=plt.cm.gray)
    ax[0].set_title('Original Image')
    
    # Show 'after' image
    ax[1].imshow(frangi(im[9]), cmap=plt.cm.gray)
    ax[1].set_title('Frangi Filter on Image\n~')

    for a in ax:
        a.axis('off')

    plt.tight_layout()
    plt.show()

def entireFile():
    # tif file is read using 'tifffile' plugin
    im = io.imread("data.tif", plugin='tifffile')
    fig = plt.figure(figsize=(85, 85))

    for i in range(len(im)):
        sub = fig.add_subplot(len(im), 10, i + 1)
        sub.imshow(frangi(im[i]), interpolation='nearest', cmap=plt.cm.gray)
        sub.set_title('#' + str(i + 1))
        sub.axis('off')
    
    fig.tight_layout()
    plt.show()

entireFile()