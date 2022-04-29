import cv2 as cv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
import scipy
from scipy.signal import find_peaks
from PIL.ImageQt import ImageQt 
from PIL import Image
from PyQt5.QtGui import QPixmap
#import utlis

from img_processing import *

### Main processing function
def get_processed_array(img):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (0,0), 2)

    ### Image separation
    img_left, img_right = img_separator (blur)
    
    ### Chip img processing
    binary_chip = adapt_thresh_otsu(img_left)
    contour_chip = get_contours(binary_chip)
    angled_line_chip, line_params_chip = draw_angle_line(contour_chip, True, 'last', 10, 2)
    
    ### Fiber img processing
    if background_profiler(img_right) >= 150:
        contrast_enhanced_fiber = contrast_enhancer(img_right)
    else:
        contrast_enhanced_fiber = img_right.copy()
    
    binary_fiber = adapt_thresh_otsu(contrast_enhanced_fiber)
    contour_fiber = get_contours(binary_fiber)
    angled_line_fiber, line_params_fiber = draw_angle_line(contour_fiber, False, 'all', 10, 6)
    
    ### Calculate angle between chip edge and fiber axis
    if (line_params_chip[0] is None) | (line_params_fiber[0] is None):
        chip_fiber_angle = 'Cannot determine angle'
    else:
        chip_fiber_angle = 'Angle: ' + get_angle(line_params_chip[0], line_params_fiber[0])
    
    processed = img_join(angled_line_chip, angled_line_fiber) # if we want to show angled line img
    # processed = img_join(contour_chip, contour_fiber) # if we want to show only contour img
    return add_text(processed, chip_fiber_angle)

def get_peaks(processed, y):
    if (len(processed.shape) > 2):
        processed = cv.cvtColor(processed, cv.COLOR_BGR2GRAY)
    
    ### Find peaks along a horizontal line y
    peaks, properties = find_peaks(processed[y,:], prominence=5) 
    return peaks

def convertCvImage2QtImage(cv_img):
    if(len(cv_img.shape)<2):
        rgb_image = cv.cvtColor(cv_img, cv.COLOR_GRAY2RGB)
    else:
        rgb_image = cv_img.copy()
    PIL_image = Image.fromarray(rgb_image).convert('RGB')
    return QPixmap.fromImage(ImageQt(PIL_image))


if __name__ == "__main__":

    def get_array(file):
        return cv.imread(file)

    def get_canny_edge(img):
        canny = cv.Canny(img, 10, 15)
        return canny

    def get_adaptive_binary(img):
        th = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY_INV,21,2)
        erode = cv.erode(th, np.ones((5,5)), iterations=1)
        return erode

    def get_binary_array(img):
        segment = segment_identifier(img)
        ### Average intensity of each segment
        left_mean = np.mean(img[:,:int(segment[1])])
        right_mean = np.mean(img[:,int(segment[2]):])

        ret_left, thresh_left = cv.threshold(img, left_mean+10, 255, cv.THRESH_BINARY)
        ret_right, thresh_right = cv.threshold(img, right_mean+20, 255, cv.THRESH_BINARY_INV)
        return cv.bitwise_xor(thresh_left, thresh_right, mask = None)

    def draw_profiling_line(img, y):
        imgLine = img.copy()
        cv.line(imgLine, (0, y), (img.shape[0], y), (255, 255, 255), thickness=2, lineType=cv.LINE_AA);
        
        return imgLine

    def create_plot(contoured, peaks, y):
        fig = plt.Figure(figsize=(6,5), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(peaks, contoured[y,:][peaks], "x", c="red")
        ax.plot(range(0,contoured.shape[0]), contoured[y,:])
        ax.set_title('Profiling of grayscale along the line')
        ax.set_ylabel('Grayscale intensity')
        ax.set_xlabel('Pixel')
        ax.set_ylim([-5,260]) ### Grayscale from 0 to 255

        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        buf = canvas.buffer_rgba()
        plot = cv.cvtColor(np.asarray(buf),cv.COLOR_RGB2BGR)
        return plot


    ### Original image
    img = get_array('Photos/Photo_Fiber_Obj_10X.tif')
    cv.imshow('Original', img)
    
    ### Processed array
    processed = get_processed_array(img) 


    ### Converting to grayscale
    #gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    #cv.imshow('Gray', gray)


    ### Blur
    #blur = cv.GaussianBlur(img, (0,0), cv.BORDER_DEFAULT)
    #cv.imshow('Blur',blur)


    ### Edge cascades / only converts edge not interiors
    #canny = cv.Canny(img, 125, 125)
    #canny = cv.Canny(blur, 125, 125)
    #cv.imshow('Canny edges', canny)


    ### Dilating the image
    #dilated = cv.dilate(canny, (3,3), iterations=1)
    #cv.imshow('Dilated', dilated)


    ### Erode
    #erode = cv.erode(canny, np.ones((5,5)), iterations=5)
    #cv.imshow('Erode', erode)


    ### Binary threshold
    #ret, thresh1 = cv.threshold(gray, 110, 255, cv.THRESH_BINARY)
    #thresh2 = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,11,7)
    #cv.imshow('Thresh1',thresh1)
    #cv.imshow('Thresh2',thresh2)


    ### Contour drawing based on binary image
    #blank = np.zeros(img.shape[:2], dtype = 'uint8')
    #cv.imshow('Blank',blank)
    #contours, hierarchies = cv.findContours(thresh1, cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)

    #utlis.getContours(img,showCanny=True)

    #contours, hierarchies = cv.findContours(thresh1, cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
    #print(f'{len(contours)} contour(s) found!')

    #cv.drawContours(blank, contours, -1, (255,255,255), 1)
    #cv.imshow('Contours Drawn', blank)


    ### Profiling on the line
    #grayLine = draw_profiling_line(gray, y=250) # draw a line on a copy of original gray image 
    #blankLine = draw_profiling_line(blank, y=250) # draw a line on a copy of contour image

    #cv.imshow('Mosfet Grayscale with Profiling line',grayLine)
    #cv.imshow('Contours Drawn with Profiling line', blankLine)

    cv.imshow('Processed', processed)
    cv.waitKey(0)