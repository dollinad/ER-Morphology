from skimage.filters import frangi, hessian
from PIL import Image
from skimage import io
from skimage import feature
import numpy as np
import matplotlib.pyplot as plt
import random
import matlab.engine
import os
eng = matlab.engine.start_matlab()


def getEigs(im):
    I = np.array(im)
    frangiImg = frangi(I)

    H_elems = feature.hessian_matrix(frangiImg, sigma=1, mode='constant', cval=0, order='rc')
    eigVals = feature.hessian_matrix_eigvals(H_elems)
    
    return eigVals, frangiImg

def getEigs3D(filename, num_slices):
    Lambda1, Lambda2, Lambda3 = eng.get_eig_vals_3D(filename, num_slices, nargout=3)
    return Lambda1, Lambda2, Lambda3

def highlight_3D(filename):
    im = Image.open(filename)
    width, height = im.size
    num_slices = 5 #im.n_frames

    # Lambda1 < Lambda2 < Lambda3
    Lambda1, Lambda2, Lambda3 = getEigs3D(filename, num_slices)

    tube = 0
    sheet = 0

    # convert to numpy arrays
    Lambda1 = np.array(Lambda1._data).reshape((width, height, num_slices))
    Lambda2 = np.array(Lambda2._data).reshape((width, height, num_slices))
    Lambda3 = np.array(Lambda3._data).reshape((width, height, num_slices))  
    
    tempIm = im
    images = []
    for z in range(num_slices):
        im = tempIm
        im.seek(z)
        im.mode = 'I'
        im = im.point(lambda i:i*(1./256)).convert('RGB')
        images.append(im)

    for z in range(num_slices):
        im = images[z]
        for x in range(width):
            for y in range(height):
                # L1 < L2 < L3
                L3 = Lambda3[y, x, z]
                L2 = Lambda2[y, x, z]
                L1 = Lambda1[y, x, z]
                
                if(x == 1000 and y == 1000 and z == 0):
                    print(L3)
                    print(L2)
                    print(L1)
                highVal = 1E-8
                lowVal = 1E-12

                #check tube / sheet conditions
                HHL = (L3 >= highVal) and (L2 >= highVal) and (abs(L1) <= lowVal)
                HHL2 = (L3 <= -highVal) and (L2 <= -highVal) and (abs(L1) <= lowVal)

                HLL = (L3 >= highVal) and (L2 < lowVal or L2 > -lowVal) and (abs(L1) <= lowVal)
                HLL2 = (L3 <= -highVal) and (L2 < lowVal or L2 > -lowVal) and (abs(L1) <= lowVal)

                is_tube = HHL or HHL2
                is_sheet = HLL or HLL2

                if is_tube:
                    im.putpixel((y, x), (255, 0, 0)) # tube
                    tube += 1
                elif is_sheet:
                    im.putpixel((y, x), (0, 255, 0)) # sheet
                    sheet += 1
    
    im = images[0]

    plt.imshow(im)
    plt.title('Eigen highlighting')
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    

def highlight(fileName, page):
    im = Image.open(fileName)

    im.seek(page)

    tempIm = im.copy()
    tempIm.mode = 'I'
    tempIm = tempIm.point(lambda i:i*(1./256)).convert('RGB')

    eigVals, frangiImg = getEigs(im)    
    
    im = tempIm
    original = tempIm.copy()

    
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

    # final_img = getAvg(original)

    width, height = im.size

    for x in range(width):
        for y in range(height):
            # L1 < L2
            L3 = eigVals[0, x, y]
            L2 = eigVals[1, x, y]
            
            highVal = 1E-7
            lowVal = 1E-12

            # is_tube = abs(L1) < lowVal and abs(L2) > highVal
            # is_sheet = abs(L1) < lowVal and abs(L2) < lowVal
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
        


    fig, ax = plt.subplots(ncols=1)
    
    # ax[0].imshow(original)
    # ax[0].set_title('Original Image')
    
    # ax[1].imshow(frangiImg)
    # ax[1].set_title('Frangi Image')

    ax[0].imshow(im)
    ax[0].set_title('Eigen highlighting')

    for a in ax:
        a.axis('off')
    plt.tight_layout()
    plt.show()
    return fig

highlight_3D("Best/STED HT1080 siCTRL. Decon_Series008_decon_z00_ch02.tif")