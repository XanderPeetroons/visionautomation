### Import library
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy.signal import find_peaks
import math
import pwlf

from img_separator import *

def contrast_enhancer(img, gamma = 14):
    ### When gamma<1, the original dark regions will be brighter and he. histogram will be shifted to the right
    ### Whereas it will be the opposite with gamma>1.
    lookUpTable = np.empty((1,256), np.uint8)
    for i in range(256):
    	lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
    enhanced = cv.LUT(fiber, lookUpTable)
    return enhanced

def background_profiler(img):
    ### Vertical profiling to calculate the background grayscale intensity.
    ### If the background is too bright (i.e. > 127), contrast_enhancer must be used.

    x = np.array(list(np.mean(img[j,:]) for j in range(0,img.shape[0])))
    peaks, _ = find_peaks(x, prominence=15)

    first_peak = peaks[0]
    last_peak = peaks[len(peaks)-1]
    
    ### margin of 50 pixels
    background= np.concatenate((img[:first_peak-50,:].ravel(),img[last_peak+50:,:].ravel()))
    return np.median(background)

def get_text(img, text):
    imageText = img.copy()
    fontScale = 2.3
    fontFace = cv.FONT_HERSHEY_PLAIN
    fontColor = (255, 255, 255)
    fontThickness = 2

    cv.putText(imageText, text, (0, img.shape[0]), fontFace, fontScale, fontColor, fontThickness, cv.LINE_AA)
    return imageText

if __name__ == "__main__":

    def get_array(file):
        return cv.imread(file)

    def rescale(img, scale = 0.75):
        width = int (img.shape[1]*scale)
        height = int (img.shape[0]*scale)

        dimensions = (width,height)

        return cv.resize(img, dimensions, interpolation=cv.INTER_AREA)
    
    def adapt_thresh_otsu(img):
        ret1, th1 = cv.threshold(img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        return th1

    def get_contours_array(img):
        blank = np.zeros(img.shape, dtype = 'uint8')
        contours, hierarchies = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cv.drawContours(blank, contours, -1, (255,255,255), thickness=2)
        return blank
    
    
    ### Segment the image
    
    array = get_array('Photos/Photo_Fiber_Obj_50X.tif')
    gray = cv.cvtColor(array, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray,(0,0),2)  ##box

    img_left, img_right = img_separator (blur)
    fiber = rescale(img_right, scale=0.48)
    
    if background_profiler(fiber) >= 150:
        fiber = contrast_enhancer(fiber)
    
    binary_fiber = adapt_thresh_otsu (fiber)
    contour_fiber = get_contours_array(binary_fiber)
    text, data = get_angle(contrast_enhancer(fiber), 'all', 'vertical', 10)
    cv.imshow('Binary', binary_fiber)
    cv.imshow('Contour', get_text(contour_fiber, text))
    

    cv.waitKey(0)