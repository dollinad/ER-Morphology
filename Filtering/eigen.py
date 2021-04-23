from skimage.filters import frangi, hessian
from PIL import Image
from skimage import io
from skimage import feature
import numpy as np
import matplotlib.pyplot as plt
import random
import matlab.engine
import os
import cv2
import math
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
    num_slices = 2 #im.n_frames
    # cv2_im = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    # eigVals, frangiImg = getEigs(cv2_im)

    # Lambda1 < Lambda2 < Lambda3
    Lambda3, Lambda2, Lambda1 = getEigs3D(filename, num_slices)

    tube = 0
    sheet = 0
    highVal = 1E-8
    lowVal = 1E-10

    # convert to numpy arrays
    Lambda1 = np.array(Lambda1._data).reshape((num_slices, width, height))
    Lambda2 = np.array(Lambda2._data).reshape((num_slices, width, height))
    Lambda3 = np.array(Lambda3._data).reshape((num_slices, width, height))
    
    tempIm = im
    images = []

    for z in range(1):
        im = tempIm
        im.seek(z)
        im.mode = 'I'
        im = im.point(lambda i:i*(1./256)).convert('RGB')
        for x in range(width):
            for y in range(height):
                # L1 < L2 < L3
                # sort eigenvalues
                lambdas = [Lambda1[z, y, x], Lambda2[z, y, x], Lambda3[z, y, x]]
                lambdas.sort
                if(x == 671 and y == 942):
                    print(lambdas)
                L3 = lambdas[0]
                L2 = lambdas[1]
                L1 = lambdas[2]

                #check tube / sheet conditions

                if abs(L3) > abs(L1)*2 and abs(L2) > abs(L1)*2 and L1*L2 > 0 and  im.getpixel((y,x)) != (0, 0, 0):
                    im.putpixel((y, x), (255, 0, 0)) # tube
                    tube += 1
        images.append(im)

    im = images[0]


    plt.imshow(im)
    plt.title('Eigen highlighting')
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    

def highlight(fileName, page):
    im = Image.open(fileName)
    im.seek(page)
    #im=crop_center(im, 1050, 400)
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
    L2_list=[]
    L3_list=[]
    for x in range(height):
        for y in range(width):
            L3 = eigVals[0, x, y]
            L2 = eigVals[1, x, y]
            L2_list.append(L2)
            L3_list.append(L3)
            # HH = (L3 >= highVal) and (L2 >= highVal)
            # HH2 = (L3 <= -highVal) and (L2 <= -highVal)
            # HL = (L3 >= highVal) and (L2 < lowVal or L2 > -lowVal)
            # HL2 = (L3 <= -highVal) and (L2 < lowVal or L2 > -lowVal)
            if ((abs(L3) < abs(L2)) and (L3>0)):
                im.putpixel((y, x), (255, 0, 0)) # tube
                tube += 1


    kwargs = dict(alpha=0.5, bins=1000)
    plt.hist(L2_list, **kwargs, color='g', label='L2')
    plt.hist(L3_list, **kwargs, color='b', label='L3')
    plt.show()

    fig, ax = plt.subplots(ncols=3)
    ax[0].imshow(original)
    ax[0].set_title('Original Image')
    ax[1].imshow(frangiImg)
    ax[1].set_title('Frangi Image')
    ax[2].imshow(im)
    ax[2].set_title('Eigen highlighting')
    plt.show()
    for a in ax:
        a.axis('off')
    return fig

highlight_3D("Best/STED HT1080 siCTRL. Decon_Series008_decon_z00_ch02.tif")