import cv2 as cv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
import scipy
from scipy.signal import find_peaks
#import utlis

from img_separator import segment_identifier

def get_array(file):
    return cv.imread(file)

def get_canny_edge(img):
    canny = cv.Canny(img, 10, 15)
    return canny

def get_adaptive_binary(img):
    th = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY_INV,21,2)
    return th

def get_binary_array(img):
    segment = segment_identifier(img)
    ### Average intensity of each segment
    left_mean = np.mean(img[:,:int(segment[1])])
    right_mean = np.mean(img[:,int(segment[2]):])

    ret_left, thresh_left = cv.threshold(img, left_mean+10, 255, cv.THRESH_BINARY)
    ret_right, thresh_right = cv.threshold(img, right_mean+20, 255, cv.THRESH_BINARY_INV)
    return cv.bitwise_xor(thresh_left, thresh_right, mask = None)

def get_contours_array(img):
    blank = np.zeros(img.shape[:2], dtype = 'uint8')
    contours, hierarchies = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    cv.drawContours(blank, contours, -1, (255,255,255), thickness=2)
    return blank

def get_processed_array(img):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (7,7), cv.BORDER_DEFAULT)
    
    ### Canny edge
    # processed = get_canny_edge(blur)
    
    ### Adaptive threshold

    ### Binary + contour
    processed = get_contours_array(get_binary_array(blur))
    return processed

def draw_profiling_line(img, y):
    imgLine = img.copy()
    cv.line(imgLine, (0, y), (img.shape[0], y), (255, 255, 255), thickness=2, lineType=cv.LINE_AA);
    
    return imgLine

def get_peaks(contoured, y):
    ### find peaks along a horizontal line y
    peaks, properties = find_peaks(contoured[y,:], prominence=5) 
    return peaks

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


if __name__ == "__main__":
    ### Original image
    img = cv.imread('Photos/mosfet.jpg') #image size is 640x640
    #cv.imshow('Mosfet',img)


    ### Converting to grayscale
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    #cv.imshow('Gray', gray)


    ### Blur
    #blur = cv.GaussianBlur(img, (7,7), cv.BORDER_DEFAULT)
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
    ret, thresh1 = cv.threshold(gray, 110, 255, cv.THRESH_BINARY)
    #thresh2 = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,11,7)
    #cv.imshow('Thresh1',thresh1)
    #cv.imshow('Thresh2',thresh2)


    ### Contour drawing based on binary image
    blank = np.zeros(img.shape[:2], dtype = 'uint8')
    #cv.imshow('Blank',blank)
    #contours, hierarchies = cv.findContours(thresh1, cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)

    #utlis.getContours(img,showCanny=True)

    contours, hierarchies = cv.findContours(thresh1, cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
    #print(f'{len(contours)} contour(s) found!')

    cv.drawContours(blank, contours, -1, (255,255,255), 1)
    #cv.imshow('Contours Drawn', blank)


    ### Profiling on the line
    grayLine = gray.copy()
    blankLine = blank.copy()

    cv.line(grayLine, (0, 250), (640, 250), (255, 255, 255), thickness=2, lineType=cv.LINE_AA) # draw a line on a copy of original gray image 
    cv.line(blankLine, (0, 250), (640, 250), (255, 255, 255), thickness=2, lineType=cv.LINE_AA) # draw a line on a copy of contour image

    cv.imshow('Mosfet Grayscale with Profiling line',grayLine)
    cv.imshow('Contours Drawn with Profiling line', blankLine)

    peaks, properties = find_peaks(blank[250,0:640], prominence=3) # find peaks along a horizontal line of 250th pixel

    fig = plt.Figure(figsize=(6,5), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(peaks, blank[250,0:640][peaks], "x", c="red")
    ax.plot(range(0,640), blank[250,0:640])
    ax.set_title('Profiling of grayscale along the line')
    ax.set_ylabel('grayscale intensity')
    ax.set_xlabel('pixel')
    ax.set_ylim([-5,260])

    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    buf = canvas.buffer_rgba()
    plot = cv.cvtColor(np.asarray(buf),cv.COLOR_RGB2BGR)
    cv.imshow('Profiling', plot)
    cv.waitKey(10000)