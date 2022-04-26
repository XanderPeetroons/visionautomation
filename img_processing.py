### Import library
from tkinter import Image
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
from sklearn.mixture import GaussianMixture 
from PIL import Image

### Basic functions

def get_array(file):    #I don't know why this is not imported
    return cv.imread(file)

def rescale(img, scale = 0.75):
    width = int (img.shape[1]*scale)
    height = int (img.shape[0]*scale)

    dimensions = (width,height)

    return cv.resize(img, dimensions, interpolation=cv.INTER_AREA)

def canny_edge (img):
    edges = cv.Canny(img,10,50) #Arguments:  1) input image, 2) minVal, 3) maxVal, 4) aperture size (default = 3), 5) L2gradient
    return edges

### Image treatment

def contrast_enhancer(img, gamma = 14):
    ### When gamma<1 (contrast factor), the original dark regions will be brighter and the histogram will be shifted to the right
    ### Whereas it will be the opposite with gamma>1.
    ### Image argument in grayscale

    lookUpTable = np.empty((1,256), np.uint8) # new array with a given shape and type
    for i in range(256):
    	lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255) #array with max values of 0 & 255
    enhanced = cv.LUT(img, lookUpTable) # new color map
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

def adapt_thresh_bin (img,x,y):
    ret1, th1 = cv.threshold(img, 127, 255, cv.THRESH_BINARY)
    th2 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,x,y) #number of pixels
    th3 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY,x,y)

    return th1, th2, th3

def adapt_thresh_inv_bin (img,x,y):
    ret1, th1 = cv.threshold(img, 127, 255, cv.THRESH_BINARY_INV)
    th2 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV,x,y)
    th3 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV,x,y)

    return th1, th2, th3

def adapt_thresh_trunc (img):
    ret1, th1 = cv.threshold(img, 127, 255, cv.THRESH_TRUNC)
    #th2 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_TRUNC,11,2)
    #th3 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_TRUNC,11,2)

    return th1#, th2, th3

def adapt_thresh_tozero (img):
    ret1, th1 = cv.threshold(img, 127, 255, cv.THRESH_TOZERO)
    #th2 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_TOZERO,11,2)
    #th3 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_TOZERO,11,2)

    return th1#, th2, th3

def adapt_thresh_inv_tozero(img):
    ret1, th1 = cv.threshold(img, 127, 255, cv.THRESH_TOZERO_INV)
    th2 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_TOZERO_INV,12,2)
    th3 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_TOZERO_INV,12,2)

    return th1, th2, th3

def adapt_thresh_otsu(img):
    ret1, th1 = cv.threshold(img, 127, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    #th2 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY + cv.THRESH_OTSU,11,2)
    #th3 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY + cv.THRESH_OTSU,11,2)

    return th1 #, th2, th3

### Additional image treatments

def sobel_edge (blur):
    sobelx = cv.Sobel(blur, ddepth=cv.CV_64F, dx=1, dy=0, ksize=3)
    sobely = cv.Sobel(blur, ddepth=cv.CV_64F, dx=0, dy=1, ksize=3)
    sobelxy = cv.Sobel(blur, ddepth=cv.CV_64F, dx=1, dy=1, ksize=3)
    return sobelx, sobely, sobelxy

def get_contours (img):
    contours, hierarchies = cv.findContours(img,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_NONE)
    blank = np.zeros(img.shape[:2], dtype = 'uint8')
    cv.drawContours(blank, contours,-1, (255,255,255), thickness=2)
    return blank

### Other function tools to process

### Some definitions:
### Kernel: matrix that defines size of convolution, weights applied and an anchor point
### Convolutions: mathematical operations between two functions that create a third function. In OpenCV

def segment_identifier(img, n_segments=3):

    x = np.arange(0, img.shape[1])
    y = np.array(list(np.mean(img[:,j]) for j in range(0,img.shape[1])))
    
    my_pwlf = pwlf.PiecewiseLinFit(x, y)
    return my_pwlf.fit(n_segments)

def img_separator(img, margin = 50):
    ### margin of 50 pixel
    segment = segment_identifier(img)
    mid = int((segment[1]+segment[2])/2)

    img_left = img[:, :mid+50] 
    img_right = img[:, mid-50:]
    return img_left, img_right

def img_join(img_left, img_right, margin = 50):
    img1 = img_left[:, :img_left.shape[1]-margin] 
    img2 = img_right[:, margin:]
    new_image = np.concatenate((img1, img2), axis = 1)
    return new_image

def add_text(img, text):
    imageText = img.copy()
    fontScale = 10
    fontFace = cv.FONT_HERSHEY_PLAIN
    fontColor = (0, 0, 0)
    fontThickness = 8
    text_color_bg=(255, 255, 255)

    text_size, _ = cv.getTextSize(text, fontFace, fontScale, fontThickness)
    text_w, text_h = text_size
    cv.rectangle(imageText, (0, img.shape[0]), (text_w, img.shape[0] - text_h), text_color_bg, -1)
    cv.putText(imageText, text, (0, img.shape[0]), fontFace, fontScale, fontColor, fontThickness, cv.LINE_AA)
    return imageText
    
def draw_angle_line(img, chip_img = True, peak_position = 'last', step = 20, n_components=3):
    ### Peak position (from left to right or top to bottom): first, last or all
    ### Step: sampling the pixel (get 1 peak for every "step" pixel)
    ### No. of components: parameter for Gaussian Mixture
    
    coord_data = []
    peak_data = []
    
    if chip_img == True:
        s = 0
    else:
        s = 1

    for j in range(0, img.shape[s], step):
        if s == 0:
            p = img[j,:]
        elif s == 1:
            p = img[:,j]
        
        peaks, _ = find_peaks(p, prominence=50)
        if len(peaks) == 0:
            continue
        
        first_peak = peaks[0]
        last_peak = peaks[len(peaks)-1]

        if (peak_position == 'last'):
            coord_data.append([j])
            peak_data.append([last_peak])
        elif (peak_position == 'first'):
            coord_data.append([j])
            peak_data.append([first_peak])
        elif (peak_position == 'all'):
            coord_data.append([j]*len(peaks))
            peak_data.append(peaks)
    data = [[item for sublist in coord_data for item in sublist],
            [item for sublist in peak_data for item in sublist]]

    clustering = GaussianMixture(n_components=n_components)
    X = np.array([[i,j] for i,j in zip(data[0], data[1])])
    labels = clustering.fit_predict(X)
    min_std = 1.0
    r = 0.0
    line_params = [None, None]

    for j in set(labels):
        xy = X[labels == j]
        if len(xy) > 20:
            slope, intercept, r_value, p_value, std_err = linregress(xy[:,0], xy[:,1])
            # print(j, slope, intercept, r_value, p_value, std_err) 
            if (std_err <= min_std) & (r_value > 0):
                min_std = std_err
                r = r_value
                line_params = [slope, intercept]
                deg = np.arctan(slope)/np.pi*180
    try:
        x_min = np.array([data[0]]).min()
        x_max = np.array([data[0]]).max()
        imgLine = img.copy()
        # imgLine = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
        slope = line_params[0]
        intercept = line_params[1]

        if chip_img == True:
            cv.line(imgLine, (int(slope*x_min+intercept), x_min), (int(slope*x_max+intercept), x_max),
                (255, 0, 0), thickness=6, lineType=cv.LINE_AA)
        else:
            cv.line(imgLine, (x_min, int(slope*x_min+intercept)), (x_max, int(slope*x_max+intercept)),
                (255, 0, 0), thickness=6, lineType=cv.LINE_AA)
              
        return imgLine, line_params
    except:
        return img, line_params

def get_angle(slope1, slope2):
    deg = 90 - np.arctan(slope1)/np.pi*180 - np.arctan(slope2)/np.pi*180
    return np.format_float_positional(deg, precision=2)