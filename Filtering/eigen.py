from skimage.filters import frangi, hessian
from PIL import Image
from skimage import io
from skimage import feature
import numpy as np
import tifffile 
import matplotlib.pyplot as plt

def eigenvalueTest():
    im = io.imread("data.tif", plugin='tifffile')
    frangiImg = frangi(im[12])
    originalImg = frangiImg

    fig, ax = plt.subplots(ncols=2)
    ax[0].imshow(originalImg)
    ax[0].set_title('Original Frangi')

    frangiImg = frangi(im[12])

    H_elems = feature.hessian_matrix(frangiImg, sigma=1, mode='constant', cval=0, order='rc')
    eigVals = feature.hessian_matrix_eigvals(H_elems)

    greaterThanZero = 0

    for x in range(0, frangiImg.shape[0]):
        for y in range(0, frangiImg.shape[1]):
            if eigVals[-1, x, y] > 1E-8:
                frangiImg[x, y] = 230
                greaterThanZero += 1

    print(greaterThanZero, "/", frangiImg.size, "pixels have an eigenvalue greater than zero")

    ax[1].imshow(frangiImg)
    ax[1].set_title('Eigen Frangi')

    for a in ax:
        a.axis('off')

    plt.tight_layout()
    plt.show()

eigenvalueTest()
