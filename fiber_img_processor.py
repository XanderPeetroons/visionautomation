### Import library
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy.signal import find_peaks
import math
import pwlf

from img_processing import *

if __name__ == "__main__":

    def get_array(file):
        return cv.imread(file)

    ### Segment the image
    
    array = get_array('Photos/Photo_Fiber_Obj_10X.tif')
    gray = cv.cvtColor(array, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray,(0,0),2)  ##box

    img_left, img_right = img_separator (blur)
    
    if background_profiler(img_right) >= 150:
        contrast_enhanced_fiber = contrast_enhancer(img_right)
    else:
        contrast_enhanced_fiber = img_right.copy()
    
    binary_fiber = adapt_thresh_otsu(contrast_enhanced_fiber)
    contour_fiber = get_contours(binary_fiber)
    # text, data, line_params = get_angle(contour_fiber, 'all', 'vertical', 20,4)

    text, data, line_params = get_angle(contrast_enhancer(contrast_enhanced_fiber),
        'all', 'vertical', 10, 6)
    
    angled_line_fiber = draw_angle_line(contour_fiber, data, line_params)
    cv.imshow('Binary', rescale(binary_fiber, 0.48))
    cv.imshow('Contour', rescale(add_text(angled_line_fiber, text),0.48))
    

    cv.waitKey(0)