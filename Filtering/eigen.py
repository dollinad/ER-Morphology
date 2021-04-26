"""
Filename: eigen.py
Authors: C. Way, D. Dodani, D. Lekovic, S. Ghorpade
Description: File containing all highlighting operations and console UI
"""

# Sci-kit image imports
from skimage.filters import frangi, hessian
from skimage import io, feature
from sklearn.cluster import KMeans

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import random
import matlab.engine
import os
import time
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
def getEigs_2D(im):
    I = np.array(im)
    frangiImg = frangi(I)
    H_elems = feature.hessian_matrix(frangiImg, sigma=1, mode='constant', cval=0, order='rc')
    eigVals = feature.hessian_matrix_eigvals(H_elems)
    return eigVals, frangiImg

"""
getEigs_3D(im, num_slices)
    - Returns the first 3 eigenvalues generated from an image based on a num_slices slices
    - Intended to be used for 3D highlighting
    - Utilized Matlab code from D. Kroon
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
def highlight_3D(filename, method, num_slices=5, sliceIndex=0):
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
    # Lists containing original images and highlighted images
    originalImages = []
    images = []
    
    # Show Progress Bar
    print("Labeling Slices")
    bar = progressbar.ProgressBar(maxval=height*width*num_slices, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    # Calculate ratios
    isRatios = False
    if method == "ratios":
        print("Labeling Using Ra/Rb Conditions")
        Ra = np.divide(np.absolute(Lambda2),np.absolute(Lambda3))
        Rb = np.divide(np.absolute(Lambda1),np.sqrt(np.absolute(np.multiply(Lambda1,Lambda2))))
        isRatios = True

    # Each slice is highlighted
    tempIm = im
    for z in range(num_slices):
        im = tempIm
        im.seek(z)
        originalImages.append(im.copy())
        # Image is converted to RGB so it may be drawn on
        im.mode = 'I'
        im = im.point(lambda i:i*(1./256)).convert('RGB')
        for x in range(width):
            for y in range(height):
                if isRatios:
                    #extract pixel Ra/Rb values
                    Ra1 = Ra[z, y, x]
                    Rb1 = Rb[z, y, x]
                    if abs(Ra1) < 0.4 and abs(Rb1) > 0.4 and im.getpixel((y,x)) != (0, 0, 0):
                        im.putpixel((y,x), (255, 0, 0))
                else:
                    #extract pixel eigenvalues
                    L3 = Lambda3[z, y, x]
                    L2 = Lambda2[z, y, x]
                    L1 = Lambda1[z, y, x]

                    if math.isclose(abs(L1), 0, abs_tol=abs(0.4*L3)) and math.isclose(abs(L2), 0, abs_tol=abs(L3*0.4)) and im.getpixel((y,x)) != (0, 0, 0):
                        im.putpixel((y, x), (0, 255, 0))
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
    original = im.copy()
    tempIm = im.copy()
    tempIm.mode = 'I'
    tempIm = tempIm.point(lambda i:i*(1./256)).convert('RGB')
    eigVals, frangiImg = getEigs_2D(im)
    width, height = im.size
    
    im = tempIm
    
    # Thresholds to change
    highVal = 3.31E-7
    lowVal = -2.11E-7
    
    L1_list=[]
    L2_list=[]
    
    for x in range(width):
        for y in range(height):
            L1 = eigVals[0, x, y]
            L2 = eigVals[1, x, y]
            
            L1_list.append(L1)
            L2_list.append(L2)
            
            HH = (L1 >= highVal) and (L2 >= highVal)
            HH2 = (L1 <= -highVal) and (L2 <= -highVal)
            HL = (L1 >= highVal) and (L2 < lowVal or L2 > -lowVal)
            HL2 = (L1 <= -highVal) and (L2 < lowVal or L2 > -lowVal)
            
            if (HH or HH2 and (im.getpixel((y,x))!=(0,0,0))):
                im.putpixel((y, x), (255, 0, 0)) # tube
            elif ((HL or HL2) and (im.getpixel((y,x))!=(0,0,0))) :
                im.putpixel((y, x), (0, 255, 0)) # sheet

    # Plot showcasing the created images is shown
    fig, ax = plt.subplots(ncols=2)
    ax[0].imshow(original)
    ax[0].set_title('Original Image')
    ax[1].imshow(im)
    ax[1].set_title('Eigen Highlighting')
    
    for a in ax:
        a.axis('off')
        
    return fig

def highlight_2D_KNN(fileName, page):
    im = Image.open(fileName)
    im.seek(page)
    original = im.copy()
    tempIm = im.copy()
    tempIm.mode = 'I'
    tempIm = tempIm.point(lambda i:i*(1./256)).convert('RGB')
    eigVals, frangiImg = getEigs_2D(im)
    width, height = im.size
    
    im = tempIm
    original = tempIm.copy()
    
    # Thresholds to change
    highVal = 3.31E-7
    lowVal = -2.11E-7
    
    L1_list=[]
    L2_list=[]
    
    for x in range(width):
        for y in range(height):
            L1 = eigVals[0, x, y]
            L2 = eigVals[1, x, y]
            
            L1_list.append(L1)
            L2_list.append(L2)
            
            HH = (L1 >= highVal) and (L2 >= highVal)
            HH2 = (L1 <= -highVal) and (L2 <= -highVal)
            HL = (L1 >= highVal) and (L2 < lowVal or L2 > -lowVal)
            HL2 = (L1 <= -highVal) and (L2 < lowVal or L2 > -lowVal)
            
            if (HH or HH2 and (im.getpixel((y,x))!=(0,0,0))):
                im.putpixel((y, x), (255, 0, 0)) # tube
            elif ((HL or HL2) and (im.getpixel((y,x))!=(0,0,0))) :
                im.putpixel((y, x), (0, 255, 0)) # sheet
    
    plt.imshow(im)
    plt.axis('off')
    plt.savefig('plot.png')
    
    imfrangii = frangiImg
    time.sleep(2)
    ## Extended code from https://github.com/AbhinavUtkarsh/Image-Segmentation.git
    image1 = cv2.imread("plot.png")
    
    image = [image1]
    reshaped=[0]
    for i in range(0,1):
        reshaped[i] = image[i].reshape(image[i].shape[0] * image[i].shape[1], image[i].shape[2])

    # Number of clusters = 4, (background pixels, backgrund from plt, tubes and sheets)
    numClusters=[4]

    # KNN Code 
    clustering=[0]
    for i in range(0,1):
        kmeans = KMeans(n_clusters=numClusters[i], n_init=40, max_iter=500).fit(reshaped[i])
        clustering[i] = np.reshape(np.array(kmeans.labels_, dtype=np.uint8),
        (image[i].shape[0], image[i].shape[1]))

    sortedLabels=[[]]
    for i in range(0,1):
        sortedLabels[i] = sorted([n for n in range(numClusters[i])],
            key=lambda x: -np.sum(clustering[i] == x))

    kmeansImage=[0]
    concatImage=[[]]
    
    for j in range(0,1):
        kmeansImage[j] = np.zeros(image[j].shape[:2], dtype=np.uint8)
        for i, label in enumerate(sortedLabels[j]):
            kmeansImage[j][ clustering[j] == label ] = int((255) / (numClusters[j] - 1)) * i
        concatImage[j] = np.concatenate((image[j],193 * np.ones((image[j].shape[0], int(0.0625 * image[j].shape[1]), 3), dtype=np.uint8),cv2.cvtColor(kmeansImage[j], cv2.COLOR_GRAY2BGR)), axis=1)

    
    ## Extended code from https://github.com/AbhinavUtkarsh/Image-Segmentation.git
    imageOut = cv2.imwrite("plot.png", concatImage[0])
    time.sleep(2)
    imageSaved = cv2.imread("plot.png")
    
    # Plot showcasing the created images is shown
    fig, ax = plt.subplots(ncols=2)
    ax[0].imshow(original)
    ax[0].set_title('Original Image')
    ax[1].imshow(imageSaved)
    ax[1].set_title('KNN Image')
    
    for a in ax:
        a.axis('off')
        
    return fig

"""
ui()
    - User interface for loading TIF files from the console
"""
def ui():
    filePath = input("Path to tif file: ")
    dimension = input("2D or 3D? (2/3): ")

    if dimension == "3":
        num_slices = int(input("Number of slices to process: "))
        image_to_display = int(input("Slice to display: "))
        if image_to_display > num_slices:
            print("Image out of range")
            return
        oimages, images, fig = highlight_3D(filePath, num_slices, image_to_display)
        user_input = 1
        while(user_input != -1):
            im = images[user_input]

            plt.imshow(im)
            plt.title('Eigen highlighting')
            plt.axis('off')
            plt.tight_layout()
            plt.show()

            user_input = int(input("Image to display (-1 to exit): "))
    elif dimension == "2":
        image_to_display = input("Slice to display: ")
        highlight_2D(filePath, image_to_display)


if __name__ == "__main__":
    # ui()
    highlight_2D("../Filtering/Best/good one.tif", 1)


