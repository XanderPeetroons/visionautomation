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
from sklearn.mixture import GaussianMixture 

## Some definitions:
## Kernel: matrix that defines size of convolution, weights applied and an anchor point
## Convolutions: mathematical operations between two functions that create a third function. In OpenCV

def segment_identifier(img, n_segments=3):

    x = np.arange(0, img.shape[1])
    y = np.array(list(np.mean(img[:,j]) for j in range(0,img.shape[1])))
    
    my_pwlf = pwlf.PiecewiseLinFit(x, y)
    return my_pwlf.fit(n_segments)

def img_separator(img):
    segment = segment_identifier(img)
    mid = int((segment[1]+segment[2])/2)

    img_left = img[:, :mid+50] ### margin of 50 pixel
    img_right = img[:, mid-50:]
    return img_left, img_right

def get_angle(img, peak_position = 'last', direction = 'horizontal', step = 20):
    ### Peak position (from left to right or top to bottom): first, last or all
    ### Direction: horizontal (for chip) or vertical (for fiber)
    ### Step: sampling the pixel (get 1 peak for every "step" pixel)
    
    coord_data = []
    peak_data = []
    
    if direction == 'horizontal':
        s = 0
    elif direction == 'vertical':
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
    # plt.plot(data[0],data[1],'.')
    # plt.xlim(0,2040)
    # plt.ylim(0,2040)
    # plt.show()

    clustering = GaussianMixture(n_components=3)
    X = np.array([[i,j] for i,j in zip(data[0], data[1])])
    labels = clustering.fit_predict(X)
    min_std = 1.0
    r = 0.0

    corners = list()
    for j in set(labels):
        xy = X[labels == j]
        if len(xy) > 5:
            plt.plot(xy[:,0],xy[:,1],'.')
            plt.xlim(0,2040)
            plt.ylim(0,2040)
            plt.show()
            slope, intercept, r_value, p_value, std_err = linregress(xy[:,0], xy[:,1])
            # print(j, slope, intercept, r_value, p_value, std_err) 
            if (std_err <= min_std) & (r_value > 0):
                min_std = std_err
                r = r_value
                deg = np.arctan(slope)/np.pi*180
                # plt.plot([0,1000],[intercept,intercept+1000*slope])
                # plt.xlim(0,2040)
                # plt.ylim(0,2040)
                # plt.show()
                if abs(slope) < 0.6:
                    corners.append(xy[0,:])
                    print(corners)

        
    try:                
        return "Angle " + np.format_float_positional(90-deg, precision=2), data, corners
    except:
        return "Cannot determine the angle", data


### From discussion on Friday
if __name__ == "__main__":  ## remove this "if" to be able to import function

    def get_array(file):
        return cv.imread(file)

    def rescale(img, scale = 0.75):
        width = int (img.shape[1]*scale)
        height = int (img.shape[0]*scale)

        dimensions = (width,height)

        return cv.resize(img, dimensions, interpolation=cv.INTER_AREA)

    def canny_edge (img):
        edges = cv.Canny(img,10,50) #Arguments:  1) input image, 2) minVal, 3) maxVal, 4) aperture size (default = 3), 5) L2gradient
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

    def adapt_thresh_otsu(img):
        ret1, th1 = cv.threshold(img, 127, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        #th2 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY + cv.THRESH_OTSU,11,2)
        #th3 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY + cv.THRESH_OTSU,11,2)

        return th1 #, th2, th3

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