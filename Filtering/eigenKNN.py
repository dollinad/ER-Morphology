from skimage.filters import frangi, hessian
from PIL import Image
from sklearn.cluster import KMeans
from skimage import io
import skimage.io as skio
from skimage import feature
import cv2
import sys
import numpy as np
np.set_printoptions(threshold=sys.maxsize)
import matplotlib.pyplot as plt
import datetime
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image 
import PIL 
import time

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
    #print(eigVals)
    im = tempIm
    original = tempIm.copy()
    width, height = im.size
    tube = 0
    sheet = 0
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
                tube += 1
            elif ((HL or HL2) and (im.getpixel((y,x))!=(0,0,0))) :
                im.putpixel((y, x), (0, 255, 0)) # sheet
                sheet += 1
    #print("Tubes:", tube, "Sheets:", sheet, ". Percentage sheets:", (sheet/(sheet+tube)*100), ". Percentage tubes:", (tube/(sheet+tube)*100))
    
    plt.imshow(im)
    plt.axis('off')
    plt.style.use("dark_background")
    plt.savefig('plot.png')
    plt.show()

    
#imfrangii=highlight('__STED HT1080 siCTRL. Decon_Series005_decon_z00_ch02.tif', 7)
filename = input("Please enter sample name with .tif extension (eg sample2.tif): ")
frame = int(input("Please enter frame that you want to process (an integer from 1 to 10: "))
imfrangii=highlight(filename, frame)


## Extended code from https://github.com/AbhinavUtkarsh/Image-Segmentation.git
image1=cv2.imread("plot.png")
image=[image1]
reshaped=[0]
for i in range(0,1):
    reshaped[i] = image[i].reshape(image[i].shape[0] * image[i].shape[1], image[i].shape[2])

##Number of clusters = 4, (background pixels, backgrund from plt, tubes and sheets)
numClusters=[4]

## KNN Code 
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


# for i in range(0,1):
#     dt = datetime.datetime.now()
#     fileExtension = "png"
#     filename = (str(dt.hour)
#         + ':'+str(dt.minute) + ':'+str(dt.second)
#         + ' C_' + str(numClusters[i]) + '.' + fileExtension)
#     print(filename)
#     time.sleep(1)
cv2.imshow("Image", mat=concatImage[0])
cv2.waitKey(50000)
cv2.destroyAllWindows()

