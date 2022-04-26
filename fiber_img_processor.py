### Import library
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy.signal import find_peaks
import math
import pwlf

from img_processing import *

def get_vertical_edge(img):

    angle, _, corners = get_angle(img, 'all', 'vertical', 10)

    peak_x = []
    peak_y = []

    for j in range(0, img.shape[0], 5):
        p = img[j,:]

        peaks, _ = find_peaks(p, prominence=50)
        if len(peaks) == 0:
            continue
        # first_peak = peaks[0]
        peak_y.append(peaks)
        peak_x.append([j]*len(peaks))
    


    data = [[item for sublist in peak_x for item in sublist ],
        [item for sublist in peak_y for item in sublist ]]

    clustering = GaussianMixture(n_components=3)
    X = np.array([[i,j] for i,j in zip(data[0], data[1])])
    labels = clustering.fit_predict(X)
    for j in set(labels):
        xy = X[labels == j]
        if len(xy) > 5:
            slope, intercept, r_value, p_value, std_err = linregress(xy[:,0], xy[:,1])
            plt.plot([0,1000],[intercept,intercept+1000*slope])
            plt.xlim(0,2040)
            plt.ylim(0,2040)
            plt.show()

if __name__ == "__main__":

    def get_array(file):
        return cv.imread(file)

    ### Segment the image
    
    array = get_array('Photos/Photo_Fiber_Obj_10X.tif')
    gray = cv.cvtColor(array, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray,(0,0),2)  ##box

    img_left, img_right = img_separator (blur)
    
<<<<<<< HEAD
    binary_fiber = adapt_thresh_otsu(fiber)
    contour_fiber = get_contours_array(binary_fiber)
    # text, data, corner = get_angle(contrast_enhancer(fiber), 'all', 'vertical', 10)
    cv.imshow('Binary', binary_fiber)
    # cv.imshow('Contour', get_text(contour_fiber, text))
    
    edge = get_vertical_edge(contour_fiber)
=======
    if background_profiler(img_right) >= 150:
        contrast_enhanced_fiber = contrast_enhancer(img_right)
    else:
        contrast_enhanced_fiber = img_right.copy()
    
    binary_fiber = adapt_thresh_otsu(contrast_enhanced_fiber)
    contour_fiber = get_contours(binary_fiber)
    # text, data, line_params = get_angle(contour_fiber, 'all', 'vertical', 20,4)

    angled_line_fiber, line_params = draw_angle_line(contour_fiber, False, 'all', 10, 6)
    text = 'Angle: ' + get_angle(line_params[0], 0)
    cv.imshow('Binary', rescale(binary_fiber, 0.48))
    cv.imshow('Contour', rescale(add_text(angled_line_fiber, text),0.48))
>>>>>>> c9400a6d4c34544d74337b07d6cadbd55490a649

    cv.waitKey(0)