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
import statistics
import progressbar
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
    highVal = 1E-8
    lowVal = 1E-10

    # convert to numpy arrays
    Lambda1 = np.array(Lambda1._data).reshape((num_slices, width, height))
    Lambda2 = np.array(Lambda2._data).reshape((num_slices, width, height))
    Lambda3 = np.array(Lambda3._data).reshape((num_slices, width, height))

    
    tempIm = im
    images = []

    avg3 = np.mean(np.true_divide(Lambda3.sum(1),(Lambda3!=0).sum(1)))
    avg2 = np.mean(np.true_divide(Lambda2.sum(1),(Lambda2!=0).sum(1)))
    avg1 = np.mean(np.true_divide(Lambda1.sum(1),(Lambda1!=0).sum(1)))
    print(avg3)
    print(avg2)
    print(avg1)

    print("Labeling Slices")
    bar = progressbar.ProgressBar(maxval=height*width*num_slices, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    for z in range(num_slices):
        im = tempIm
        im.seek(z)
        im.mode = 'I'
        im = im.point(lambda i:i*(1./256)).convert('RGB')
        for x in range(width-1):
            for y in range(height-1):
                # L1 < L2 < L3
                L3 = Lambda3[z, y, x]
                L2 = Lambda2[z, y, x]
                L1 = Lambda1[z, y, x]

                if abs(L3) > avg3*0.67 and abs(L2) > avg3*0.67 and abs(L1) > avg3*0.67:
                    continue; # blob

                #check tube / sheet conditions
                threshold = 2
                if math.isclose(abs(L1), 0, abs_tol=abs(0.3*L3)) and math.isclose(abs(L2), 0, abs_tol=abs(L3*0.3)) and im.getpixel((y,x)) != (0, 0, 0):
                    im.putpixel((y, x), (0, 255, 0)) # tube
                    tube += 1
                # if abs(L3) > abs(L1)*2 and abs(L2) > abs(L1)*2 and L1*L2 > 0 and  im.getpixel((y,x)) != (0, 0, 0):
                #     im.putpixel((y, x), (255, 0, 0)) # tube
                #     tube += 1
                bar.update(z*width*height+x*height+y)
        images.append(im)
    bar.finish()
    im = images[3]

    L3 = Lambda3[3, 1407, 1118]
    L2 = Lambda2[3, 1407, 1118]
    L1 = Lambda1[3, 1407, 1118]
    print(L3)
    print(L2)
    print(L1)


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