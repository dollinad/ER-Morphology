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

def highlight_3D(filename, num_slices, image_to_display):
    im = Image.open(filename)
    width, height = im.size
    if num_slices == "all":
        num_slices = im.n_frames

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

    # Ra = np.divide(np.absolute(Lambda2),np.absolute(Lambda3))
    # Rb = np.divide(np.absolute(Lambda1),np.sqrt(np.absolute(np.multiply(Lambda1,Lambda2))))
    # Rblob = np.divide(np.absolute(np.subtract(np.multiply(2, Lambda3), np.subtract(Lambda2, Lambda3))), np.absolute(Lambda3))
    # S = np.add(Lambda3, np.add(Lambda2, Lambda1))

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
                # Ra1 = Ra[z, y, x]
                # Rb1 = Rb[z, y, x]
                # Rblob1 = Rblob[z, y, x]
                L3 = Lambda3[z, y, x]
                L2 = Lambda2[z, y, x]
                L1 = Lambda1[z, y, x]

                # if Rb1 < 0.3:
                #     continue 
                if math.isclose(abs(L1), 0, abs_tol=abs(0.4*L3)) and math.isclose(abs(L2), 0, abs_tol=abs(L3*0.4)) and im.getpixel((y,x)) != (0, 0, 0):
                    im.putpixel((y, x), (255, 0, 0)) # sheet
                # if abs(Ra1  < 0.5 and abs(Rblob1 - 1) < 0.5 and im.getpixel((y,x)) != (0, 0, 0):
                #     im.putpixel((y,x), (255, 0, 0)) #tube
                bar.update(z*width*height+x*height+y)
        images.append(im)
    bar.finish()
    return images
    

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
            L1 = eigVals[0, x, y]
            L2 = eigVals[1, x, y]
            L1_list.append(L1)
            L2_list.append(L2)
            if ((abs(L1) < abs(L2)) and (L2<0)):
                im.putpixel((y, x), (255, 0, 0)) # tube bright red 
                tube += 1
            if((abs(L1) > 0.002 and abs(L2 > 0.002)) and (L1<0 and L2<0)):
                im.putpixel((y, x), (255, 255, 51)) # tube dark yellow
            if((abs(L1) > 0.002 and abs(L2 > 0.002)) and (L1>0 and L2>0)):
                im.putpixel((y, x), (255, 255, 51)) # tube dark yellow


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

def ui():
    # filePath = input("Path to tif file: ")
    # dimension = input("2D or 3D? (2/3): ")

    # if dimension == "3":
    #     num_slices = int(input("Number of slices to process: "))
    #     image_to_display = int(input("Slice to display: "))
    #     if image_to_display > num_slices:
    #         print("Image out of range")
    #         return
    #     highlight_3D(filePath, num_slices, image_to_display)
    # elif dimension == "2":
    #     image_to_display = input("Slice to display: ")
    #     highlight(filePath, image_to_display)
    images = highlight_3D("Best/good one.tif", 5, 1)
    user_input = 1
    while(user_input != -1):
        im = images[user_input]

        plt.imshow(im)
        plt.title('Eigen highlighting')
        plt.axis('off')
        plt.tight_layout()
        plt.show()

        user_input = int(input("Image to display (-1 to exit): "))


if __name__ == "__main__":
    ui()