"""
Filename: eigen.py
Authors: C. Way, D. Dodani, D. Lekovic, S. Ghorpade
Description: File containing all highlighting operations and console UI
"""

# Sci-kit image imports
from skimage.filters import frangi, hessian
from skimage import io, feature

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import random
import matlab.engine
import os
import cv2
import math
import statistics
import progressbar

# Engine for MATLAB
eng = matlab.engine.start_matlab()

"""
getEigs_2D(image)
    - Returns the eigenvalues generated from an image
    - Intended to be used for 2D highlighting
"""
def getEigs_2D(image):
    # Convolves the image with the second derivatives of the Gaussian to compute the Hessian matrix
    H_elems = feature.hessian_matrix(image, sigma=1, mode='constant', cval=0, order='rc')
    
    # Computes the eigenvalues of the Hessian matrix and returns them in decreasing order
    eigVals = feature.hessian_matrix_eigvals(H_elems)
    
    return eigVals

"""
getEigs_3D(im, num_slices)
    - Returns the first 3 eigenvalues generated from an image based on a num_slices slices
    - Intended to be used for 3D highlighting
"""
def getEigs3D(filename, num_slices):
    Lambda1, Lambda2, Lambda3 = eng.get_eig_vals_3D(filename, num_slices, nargout=3)
    return Lambda1, Lambda2, Lambda3

"""
getFig_3D(originalImage, image, sliceIndex)
    - Returns a 2 column subplot figure
    - Shows original image at a slice index
    - Show highlighted image at a slice index
"""
def getFig_3D(originalImage, image, sliceIndex):
    fig, ax = plt.subplots(ncols=2)
    ax[0].imshow(originalImage[sliceIndex])
    ax[0].set_title('Original Image')
    ax[1].imshow(image[sliceIndex])
    ax[1].set_title('Highlighted Image')
    plt.axis('off')
    plt.tight_layout()
    
    for a in ax:
        a.axis('off')
        
    return fig

"""
highlight_3D(filename, num_slices, sliceIndex)
    - Returns original image, highlighted image, and figure
    - Loads num_slices of an image from filename
    - Highlights sheets and tubes of a 3D image
"""
def highlight_3D(filename, num_slices=5, sliceIndex=0):
    # Image is loaded
    im = Image.open(filename)
    originalImage = im
    width, height = im.size

    if num_slices == "all":
        num_slices = im.n_frames

    # Eigenvalues are calculated: Lambda1 < Lambda2 < Lambda3
    Lambda1, Lambda2, Lambda3 = getEigs3D(filename, num_slices)

    # convert to numpy arrays
    Lambda1 = np.array(Lambda1._data).reshape((num_slices, width, height))
    Lambda2 = np.array(Lambda2._data).reshape((num_slices, width, height))
    Lambda3 = np.array(Lambda3._data).reshape((num_slices, width, height))
    
    tempIm = im
    
    # Lists containing original images and highlighted images
    originalImages = []
    images = []
    
    # Progress bar
    print("Labeling Slices")
    bar = progressbar.ProgressBar(maxval=height*width*num_slices, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    
    # Each slice is highlighted
    for z in range(num_slices):
        im = tempIm
        im.seek(z)
        originalImages.append(im.copy())
        
        # Image is converted to RGB so it may be drawn on
        im.mode = 'I'
        im = im.point(lambda i:i*(1./256)).convert('RGB')
        
        # Each pixel is observed
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
    fig = getFig_3D(originalImages, images, sliceIndex)
    
    return originalImages, images, fig
    
"""
highlight_2D(filename, page)
    - Returns a figure showing the original image, Frangi image, and highlighted image
    - Highlights sheets and tubes of a 2D image
"""
def highlight_2D(fileName, page):
    im = Image.open(fileName)
    im.seek(page)
    
    # Image is converted to RGB so it may be drawn on
    tempIm = im.copy()
    tempIm.mode = 'I'
    tempIm = tempIm.point(lambda i:i*(1./256)).convert('RGB')
    
    # Frangi filter is applied
    I = np.array(im)
    frangiImg = frangi(I)
    
    # Eigenvalues are calculated
    eigVals = getEigs_2D(im)
    im = tempIm
    original = tempIm.copy()
    width, height = im.size
    
    # Counting the number of tubes and sheets
    tube = 0
    sheet = 0
    
    # L, L => no structure just noise
    # H-, L OR H+, L => sheet like
    # H+, H+ OR H-, H- => tube like
    # 
    # Based on the histogram:
    # => look at distribution of lambda
    # L is very close to zero
    # H- is farther from zero, but negative
    # H+ is closer to zero, but positive
    
    L2_list = []
    L3_list = []
    
    # Eigenvalues at each pixel are assessed
    for x in range(height):
        for y in range(width):
            L1 = eigVals[0, x, y]
            L2 = eigVals[1, x, y]
            L1_list.append(L1)
            L2_list.append(L2)
            
            # Tube is detected
            if ((abs(L1) < abs(L2)) and (L2 < 0)):
                # Tube is turned bright red 
                im.putpixel((y, x), (255, 0, 0))
                tube += 1
                
            # Sheet detected
            if ((abs(L1) > 0.002 and abs(L2 > 0.002)) and (L1<0 and L2<0)):
                # Sheet is turned dark yellow
                im.putpixel((y, x), (255, 255, 51))
                
    # Histogram of eigenvalues is shown for debugging purposes
    kwargs = dict(alpha=0.5, bins=1000)
    plt.hist(L2_list, **kwargs, color='g', label='L2')
    plt.hist(L3_list, **kwargs, color='b', label='L3')
    plt.show()
    
    # Plot showcasing the created images is shown
    
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

"""
ui()
    - User interface for loading TIF files from the console
"""
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

