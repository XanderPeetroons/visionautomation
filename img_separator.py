### Import library
import cv2 as cv
from cv2 import IMWRITE_JPEG2000_COMPRESSION_X1000
from cv2 import THRESH_BINARY
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy.signal import find_peaks
import math
import pwlf


def segment_identifier(img, n_segments=3):

    x = np.arange(0, img.shape[1])
    y = np.array(list(np.mean(img[:,j]) for j in range(0,img.shape[1])))
    
    my_pwlf = pwlf.PiecewiseLinFit(x, y)
    return my_pwlf.fit(n_segments)

def img_separator(img):
    segment = segment_identifier(img)
    mid = int((segment[1]+segment[2])/2)

    img_left = gray[:, :mid+50] ### margin of 50 pixel
    img_right = gray[:, mid-50:]
    return img_left, img_right


### From discussion on Friday
"""
Henry commented: I have to remove the import function from Example_mv01.py in order to run GUI.py
Otherwise it will yield an error of circular import. Sorry!
"""

"""

def get_array(file):
    return cv.imread(file)

def rescale(img, scale = 0.75):
    width = int (img.shape[1]*scale)
    height = int (img.shape[0]*scale)

    dimensions = (width,height)

    return cv.resize(img, dimensions, interpolation=cv.INTER_AREA)

def canny_edge (img):
    edges = cv.Canny(img,100,200)
    return edges

def adapt_thresh_bin (img):
    ret1, th1 = cv.threshold(img, 127, 255, cv.THRESH_BINARY)
    th2 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,11,2)
    th3 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY,11,2)

    return th1, th2, th3

def adapt_thresh_inv_bin (img):
    ret1, th1 = cv.threshold(img, 127, 255, cv.THRESH_BINARY_INV)
    th2 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV,11,2)
    th3 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV,11,2)

    return th1, th2, th3

def adapt_thresh_trunc (img):
    ret1, th1 = cv.threshold(img, 127, 255, cv.THRESH_TRUNC)
    th2 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_TRUNC,11,2)
    th3 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_TRUNC,11,2)

    return th1, th2, th3

def adapt_thresh_tozero (img):
    ret1, th1 = cv.threshold(img, 127, 255, cv.THRESH_TOZERO)
    th2 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_TOZERO,11,2)
    th3 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_TOZERO,11,2)

    return th1, th2, th3

def adapt_thresh_inv_tozero(img):
    ret1, th1 = cv.threshold(img, 127, 255, cv.THRESH_TOZERO_INV)
    th2 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_TOZERO_INV,12,2)
    th3 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_TOZERO_INV,12,2)

    return th1, th2, th3


### Trying additional image treatments

def sobel_edge (blur):
    sobelx = cv.Sobel(blur, ddepth=cv.CV_64F, dx=1, dy=0, ksize=3)
    sobely = cv.Sobel(blur, ddepth=cv.CV_64F, dx=0, dy=1, ksize=3)
    sobelxy = cv.Sobel(blur, ddepth=cv.CV_64F, dx=1, dy=1, ksize=3)
    return sobelx, sobely, sobelxy

def get_contours (img):
    contours = cv.findContours(img,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_NONE)
    blank = np.zeros(img.shape[:2], dtype = 'uint8')
    cv.drawContours(blank, contours,-1, (255,255,255), thickness=1)
    return blank

### Segment the image

array = get_array('Photos/Photo_Fiber_Obj_10X.tif')
gray = cv.cvtColor(array, cv.COLOR_BGR2GRAY)
blur = cv.GaussianBlur(gray,(5,5),cv.BORDER_DEFAULT)

img_left, img_right = img_separator (blur)
left_img = rescale(img_left, scale=0.48)

### Printing alternatives
cv.imshow('Left',left_img)
#cv.imshow('Canny',canny_edge(left_img))
#sobelx, sobely, sobelxy = sobel_edge(left_img)
#cv.imshow('SobelX',sobelx)
#cv.imshow('SobelY',sobely)
#cv.imshow('SobelXY',sobelxy)
#contoursonly = get_contours(canny_edge(left_img))
#cv.imshow('Dibujando los contornos',contoursonly)
th1, th2, th3 = adapt_thresh_bin (left_img)
thv1, thv2, thv3 = adapt_thresh_inv_bin (left_img)
# thk1, thk2, thk3 = adapt_thresh_trunc (left_img)
# th01, th02, th03 = adapt_thresh_tozero (left_img)
# th0v1, th0v2, th0v3 = adapt_thresh_inv_tozero (left_img)
cv.imshow('Binary', th1)
cv.imshow('Adapt Mean', th2)
cv.imshow('Adapt Gaussian', th3)
# cv.imshow('Adapt Gaussian Inv', thv3)

cv.waitKey(0)
"""
