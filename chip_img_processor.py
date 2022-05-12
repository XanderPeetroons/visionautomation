### Import library
import cv2 as cv
from cv2 import IMWRITE_JPEG2000_COMPRESSION_X1000
from cv2 import THRESH_BINARY
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy.signal import find_peaks
from scipy.stats import linregress
import math
import pwlf
from PIL import Image

from img_processing import *

if __name__ == "__main__":

    def get_array(file):
        return cv.imread(file)
  
    ### Segment the image

    array1 = get_array('Photos/Photo_Fiber_Obj_10X.tif')
    array2 = get_array('Photos/Photo_Fiber_Obj_20X.tif')
    array3 = get_array('Photos/Photo_Fiber_Obj_50X.tif')

    #cv.imshow('Original image', rescale(array, scale = 0.48))
    gray1 = cv.cvtColor(array1, cv.COLOR_BGR2GRAY)
    gray2 = cv.cvtColor(array2, cv.COLOR_BGR2GRAY)
    gray3 = cv.cvtColor(array3, cv.COLOR_BGR2GRAY)

    blur1 = cv.GaussianBlur(gray1,(5,5),cv.BORDER_DEFAULT)  ##box
    blur2 = cv.GaussianBlur(gray2,(5,5),cv.BORDER_DEFAULT)  ##box
    blur3 = cv.GaussianBlur(gray3,(5,5),cv.BORDER_DEFAULT)  ##box

    img_left1, img_right1 = img_separator (blur1)
    img_left2, img_right2 = img_separator (blur2)
    img_left3, img_right3 = img_separator (blur3)

    #left_img1 = rescale(img_left1, scale=0.25)
    #left_img2 = rescale(img_left2, scale=0.25)
    #left_img3 = rescale(img_left3, scale=0.25)

    #array = np.concatenate((left_img1,left_img2), axis=1)
    #cv.imshow('Grey original 10x & 20x', array)
    #cv.imshow('Grey original 50x', left_img3)

    ### Processing image for edges and angle calculation

    #cv.imshow('Left',left_img)
    #chip_image = canny_edge(left_img)
    canny_chip10x = canny_edge(img_left1)
    cv.imshow('Canny chip 10x',rescale(canny_chip10x, 0.48))

    #chip20x = adapt_thresh_otsu(left_img2)
    #post_chip20x = canny_edge(chip20x)
    #cv.imshow('Canny chip 20x',post_chip20x)

    #binary_chips1, binary_chips2, binary_chips3 = adapt_thresh_bin(array)
    #img50x1, img50x2, img50x3 = adapt_thresh_bin(left_img3,3,-2)    ##mean seam to be better
    binary_chip10x = adapt_thresh_otsu(img_left1)
    #cv.imshow('Binary',img50x1)
    cv.imshow('Binary chip 10x',rescale(binary_chip10x,0.48))
    #cv.imshow('Binary Gaussian',img50x3)
    
    '''
    if background_profiler(binary_chip10x) >= 150:
        binary_chip10x = contrast_enhancer(binary_chip10x)
        print('Contrast enhanced...')
    '''

    ### Calculating angle and drawing line
    contour_chip10x = get_contours(binary_chip10x)
    #angled_line_chip10x, line_params = draw_angle_line(contour_chip10x, True, 'last', 10, 2)
    #textc = 'Angle: ' + get_angle(line_params[0], 0)
    #cv.imshow('Contour chip 10x', rescale(add_text(angled_line_chip10x, textc),0.48))
    

    ### Merging processed images
    '''
    #right_img = rescale(img_right, scale=0.48)
    #new_left = chip_image[:, :(chip_image.shape[0]-50)]
    #cv.imshow('-50pix', new_left)
    #binary_fiber = adapt_thresh_otsu(right_img)

    if background_profiler(binary_chip) >= 150:
        binary_fiber = contrast_enhancer(binary_fiber)
        print('Contraste enhanced...')
    
    contour_fiber = get_contours_array(binary_fiber)
    textf, dataf = get_angle(contrast_enhancer(right_img), 'all', 'vertical', 10)
    #cv.imshow('Contour_fiber', get_text(contour_fiber, textf))

    post_process_img = img_join(chip_image,contour_fiber)  ### the 50 pixel margin is added
    cv.imshow('Joined image',post_process_img)
    '''

    cv.waitKey(0)