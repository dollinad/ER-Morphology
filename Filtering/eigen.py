from skimage.filters import frangi, hessian
from PIL import Image
from skimage import io
from skimage import feature
import numpy as np
import tifffile 
import matplotlib.pyplot as plt

def eigenvalueTest():
    im = io.imread("data.tif", plugin='tifffile')
    
    fig, ax = plt.subplots(ncols=2)
    ax[0].imshow(im[12])
    ax[0].set_title('Original')

    frangiImg = frangi(im[12])

    ax[1].imshow(frangiImg)
    ax[1].set_title('Frangi')

    H_elems = feature.hessian_matrix(frangiImg, sigma=1, mode='constant', cval=0, order='rc')
    eigVals = feature.hessian_matrix_eigvals(H_elems)

    greaterThanZero = 0

    for outerVal in eigVals:
        for innerVal in outerVal:
            if innerVal[-1] > 0:
                greaterThanZero += 1

    print(greaterThanZero, "/", frangiImg.size, "pixels have an eigenvalue greater than zero")

    for a in ax:
        a.axis('off')

    plt.tight_layout()
    plt.show()

eigenvalueTest()
