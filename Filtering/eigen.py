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
    
    return eigVals, frangiImg
    
def highlight(fileName, page):
    im = Image.open(fileName)
    im.seek(page)

    tempIm = im.copy()
    tempIm.mode = 'I'
    tempIm = tempIm.point(lambda i:i*(1./256)).convert('RGB')
    
    eigVals, frangiImg = getEigs(im)
    
    im = tempIm
    original = tempIm.copy()

    width, height = im.size
    
    tube = 0
    sheet = 0
    
    # Thresholds to change
    highVal = 1E-8
    lowVal = 1E-10
    
    # L, L => no structure just noise
    # H-, L OR H+, L => sheet like
    # H+, H+ OR H-, H- => tube like
    # 
    # histogram
    # => look at distribution of lambda

    # L is very close to zero
    # H- is farther from zero, but negative
    # H+ is closer to zero, but positive
    
    for x in range(width):
        for y in range(height):
            L3 = eigVals[0, x, y]
            L2 = eigVals[1, x, y]
            
            highVal = 1E-7
            lowVal = 1E-12

            HH = (L3 >= highVal) and (L2 >= highVal)
            HH2 = (L3 <= -highVal) and (L2 <= -highVal)

            HL = (L3 >= highVal) and (L2 < lowVal or L2 > -lowVal)
            HL2 = (L3 <= -highVal) and (L2 < lowVal or L2 > -lowVal)

            if HH or HH2:
                im.putpixel((y, x), (255, 0, 0)) # tube
                tube += 1
            elif HL or HL2:
                im.putpixel((y, x), (0, 255, 0)) # sheet
                sheet += 1

    fig, ax = plt.subplots(ncols=3)
    
    ax[0].imshow(original)
    ax[0].set_title('Original Image')
    
    ax[1].imshow(frangiImg)
    ax[1].set_title('Frangi Image')

    ax[2].imshow(im)
    ax[2].set_title('Eigen highlighting')

    for a in ax:
        a.axis('off')
    
    return fig
