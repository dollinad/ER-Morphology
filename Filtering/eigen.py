from skimage.filters import frangi, hessian
from PIL import Image
from skimage import io
from skimage import feature
import numpy as np
import matplotlib.pyplot as plt

def getEigs(im):
    I = np.array(im)
    frangiImg = frangi(I)

    H_elems = feature.hessian_matrix(frangiImg, sigma=1, mode='constant', cval=0, order='rc')
    eigVals = feature.hessian_matrix_eigvals(H_elems)
    
    return eigVals

def highlight(fileName, page):
    im = Image.open(fileName)
    im.seek(page)

    tempIm = im.copy()
    tempIm.mode = 'I'
    tempIm.point(lambda i:i*(1./256)).convert('RGB').save('temp.jpeg')

    im = Image.open('temp.jpeg')
    original = im.copy()

    eigVals = getEigs(tempIm)

    width, height = im.size

    # L, L => no structure just noise
    # H-, L OR H+, L => sheet like
    # H+, H+ OR H-, H- => tube like

    # L is very close to zero
    # H- is farther from zero, but negative
    # H+ is closer to zero, but positive
    
    for x in range(width):
        for y in range(height):
            L3 = eigVals[0, x, y]
            L2 = eigVals[1, x, y]
            
            HH = (L3 >= 1E-7) and (L2 >= 1E-7)
            HH2 = (L3 <= -1E-7) and (L2 <= -1E-7)
            
            HL = (L3 >= 1E-7) and (L2 < 1E-12 or L2 > -1E-12)
            HL2 = (L3 <= -1E-7) and (L2 < 1E-12 or L2 > -1E-12)

            if HH or HH2:
                im.putpixel((y, x), (255, 0, 0)) # tube
            elif HL or HL2:
                im.putpixel((y, x), (0, 255, 0)) # sheet


    fig, ax = plt.subplots(ncols=2)
    ax[0].imshow(original)
    ax[0].set_title('Original Image')

    ax[1].imshow(im, interpolation='nearest')
    ax[1].set_title('Eigen highlighting')

    for a in ax:
        a.axis('off')

    plt.tight_layout()
    plt.show()

highlight('data.tif', 20)
