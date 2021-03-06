### Import library
import cv2 as cv
from cv2 import IMWRITE_JPEG2000_COMPRESSION_X1000
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy.signal import find_peaks
from scipy.stats import linregress
import math
import pwlf
from sklearn.mixture import GaussianMixture 
from PIL import Image


### Some definitions:
### Kernel: matrix that defines size of convolution, weights applied and an anchor point
### Convolutions: mathematical operations between two functions that create a third function. In OpenCV

### Import image
def get_array(file):
    return cv.imread(file)

### Rescale the image during cv.imgshow
def rescale(img, scale = 0.75):
    width = int (img.shape[1]*scale)
    height = int (img.shape[0]*scale)

    dimensions = (width,height)

    return cv.resize(img, dimensions, interpolation=cv.INTER_AREA)

### Calculate background brightness by quickly detecting fiber region (not neccessary if we let user to define AOI)
def background_profiler(img):
    ### Vertical profiling to calculate the background grayscale intensity.
    ### If the background is too bright (i.e. > 127), contrast_enhancer must be used.

    x = np.array(list(np.mean(img[j,:]) for j in range(0,img.shape[0])))
    peaks, _ = find_peaks(x, prominence=15)

    if  len(peaks) > 0:
        first_peak = peaks[0]
        last_peak = peaks[len(peaks)-1]
        if (first_peak - 50 > 0) & (last_peak + 50 < img.shape[0]):
            ### margin of 50 pixels
            background= np.concatenate((img[:first_peak-50,:].ravel(),img[last_peak+50:,:].ravel()))
        else:
            background= np.concatenate((img[:first_peak,:].ravel(),img[last_peak:,:].ravel()))
        return np.median(background)
    else:
        return 0

### Enhancing contrast before performing binary conversion
def contrast_enhancer(img, gamma = 14):
    ### When gamma<1 (contrast factor), the original dark regions will be brighter and the histogram will be shifted to the right
    ### Whereas it will be the opposite with gamma>1.
    ### Image argument in grayscale

    lookUpTable = np.empty((1,256), np.uint8) # new array with a given shape and type
    for i in range(256):
        lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255) #array with max values of 0 & 255
    enhanced = cv.LUT(img, lookUpTable) # new color map
    return enhanced

### Perform canny edge detection
def canny_edge (img):
    edges = cv.Canny(img,10,50) #Arguments:  1) input image, 2) minVal, 3) maxVal, 4) aperture size (default = 3), 5) L2gradient
    return edges

def auto_canny(image, sigma=0.33):
	# compute the median of the single channel pixel intensities
	v = np.median(image)
	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv.Canny(image, lower, upper)
	# return the edged image
	return edged

### Perform sobel edge detection
def sobel_edge (blur):
    sobelx = cv.Sobel(blur, ddepth=cv.CV_64F, dx=1, dy=0, ksize=3)
    sobely = cv.Sobel(blur, ddepth=cv.CV_64F, dx=0, dy=1, ksize=3)
    sobelxy = cv.Sobel(blur, ddepth=cv.CV_64F, dx=1, dy=1, ksize=3)
    return sobelx, sobely, sobelxy

### Perform binary conversion 
def binary_threshold (img,threshold):
    ret, bin_image = cv.threshold(img, threshold, 255, cv.THRESH_BINARY)
    return bin_image

### Perform adaptive binary conversion 
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

    return ret1, th1 #, th2, th3


### Draw contour based on binary image
def get_contours (img, chip_img = True):
    thickness = 2 ### thickness of the contour line
    contours, hierarchies = cv.findContours(img,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_NONE)
    blank = np.zeros(img.shape, dtype = 'uint8')
    cv.drawContours(blank, contours, -1, (255,255,255), thickness=thickness)
    ### In case of the chip image, need to remove the midline
    if chip_img:
        # if min(blank[:, -thickness:].ravel()) == 255:
        blank[:, -thickness:] = 0
    return blank

### Detect fiber and chip region (not neccessary if we let user to define AOI)
def img_separator(img, vline, margin = 0):
    ### margin means the additional pixels before and after vline to ensure the robustness of algorithm
    ### auto-separation
    """
    x = np.arange(0, img.shape[1])
    y = np.array(list(np.mean(img[:,j]) for j in range(0,img.shape[1])))
    
    my_pwlf = pwlf.PiecewiseLinFit(x, y)
    segment = my_pwlf.fit(3)
    mid = int((segment[1]+segment[2])/2)
    """
    
    ### manual separation
    mid = vline 
    img_left = img[:, :mid+margin]
    img_right = img[:, mid-margin:]
    return img_left, img_right

### Return cropped image of the fiber and the chip using the lines defined by the user
def get_cropped_image(img, vline, topline, botline, margin=0):
    ### topline and botline should be number of pixel of the array
    # img_left, img_right = img_separator(img,vline, margin)
    height = botline-topline
    img_cropped = img[ topline:botline, max( int(vline-height/2),0 ):min( int(vline+height/2),img.shape[1] ) ]
    return img_cropped


### Join chip and fiber images into final image
def img_join(img_left, img_right, margin = 0):
    img1 = img_left[:, :img_left.shape[1]-margin] 
    img2 = img_right[:, margin:]
    new_image = np.concatenate((img1, img2), axis = 1)
    return new_image

### Add angle value as a text on image (not neccessary in the final GUI)
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
    
### Detect major axial of fiber and chip to calculate they angle
def get_axial_line(img, chip_img = True, peak_position = 'last', step = 20, n_components=2):
    ### Peak position (from left to right or top to bottom): first, last or all
    ### Step: sampling the pixel (get 1 peak for every "step" pixel)
    ### No. of components: parameter for Gaussian Mixture => tunable parameter
    ### If peak_position is either 'first' or 'last', n_components shoule be 2, else 6
    
    imgLine = img.copy()
    imgLine = cv.cvtColor(imgLine, cv.COLOR_GRAY2BGR)

    coord_data = []
    peak_data = []
    
    if chip_img == True:
        s = 0
    else:
        s = 1

    ### To deal with scaled image before processing. Algorithm requires sufficient points to run accurately.
    if int(img.shape[s]/step) < 50:
        step = int(img.shape[s]/51)

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

    X = np.array([[i,j] for i,j in zip(data[0], data[1])])
    min_sample_size = 10 ### minimum no. of point to fit a line
    line_params = [None, None] ### to store slope and interception of the line
    labels = [] ### clustering label
    good_labels = [] ### clustering label of the line which is used for 2nd algo of finding distance
    try: 
        clustering = GaussianMixture(n_components=n_components, random_state = 3)
        ### All points are clustered into n_components labels using Gaussian Mixture.
        ### Gaussian Mixture can cluster linear lines very well.
        ### Random_state is a random seed, pass a value to have reproducible output across multiple function calls
        labels = clustering.fit_predict(X)
        min_std = 1.0
        r = 0.0
        std_thresh = 0.2
        
        for j in set(labels):
            xy = X[labels == j]
            if len(xy) > min_sample_size:
                slope, intercept, r_value, p_value, std_err = linregress(xy[:,0], xy[:,1])
                # print(j, slope, intercept, r_value, p_value, std_err) 
                if (std_err <= min_std) & (r_value > 0):
                    min_std = std_err
                    r = r_value
                    line_params = [slope, intercept]
                if std_err <= std_thresh:
                    good_labels.append(j)

        x_min = np.array([data[0]]).min()
        x_max = np.array([data[0]]).max()
        y_min = np.array([data[1]]).min()
        y_max = np.array([data[1]]).max()
        y_mean = (y_min+y_max)/2
        
        slope = line_params[0]
        intercept = line_params[1]

        if chip_img == True:
            cv.line(imgLine, (int(slope*x_min+intercept), x_min), (int(slope*x_max+intercept), x_max),
                (0, 255, 0), thickness=5, lineType=cv.LINE_AA) ### Green
        else:
            cv.line(imgLine, (0, int(slope*x_min+y_mean)), (x_max, int(slope*x_max+y_mean)),
                (0, 0, 255), thickness=5, lineType=cv.LINE_AA) ### Red
              
        return imgLine, line_params, X, labels, good_labels
    
    except:
        return imgLine, line_params, X, labels, good_labels

### Calculate angle between 2 lines
def get_angle(slope1, slope2):
    try:
        deg = abs(90 - np.arctan(slope1)/np.pi*180 - np.arctan(slope2)/np.pi*180)
        return np.format_float_positional(deg, precision=2)
    except:
        return 'Cannot determine'

### Calculate vertical distance between point to line
def get_distance(img_right, vline, line_params_chip, quality):
    ### Corner detection:
    ### Maximum number of corners to return. If there are more corners than are found, the strongest of them is returned.
    ### Parameter characterizing the minimal accepted quality of image corners => tunable parameter
    ### Minimum possible Euclidean distance between the returned corners.
    ### Size of an average block for computing a derivative covariation matrix over each pixel neighborhood/

    ### To detect corner in fiber tip only
    height = img_right.shape[0]
    cropped = img_right[:, :int(height/2)]
    feature_params = dict( maxCorners = 100,
                       qualityLevel = quality,
                       minDistance = int(height/20),
                       blockSize = 9)
    corners = cv.goodFeaturesToTrack(cropped, **feature_params)

    ### Calculate distance
    slope = line_params_chip[0]
    intercept = line_params_chip[1]

    try:
        corners = corners.reshape(-1,2)
        corners[:,0] = corners[:,0]+vline # shift the x-value by vline
        distance = []
        for x, y in np.float32(corners):
            ### x = ay+b => -x +ay + b = 0
            distance.append(abs(-x +slope*y + intercept) / math.sqrt(slope*slope + 1) )
        d = min(distance)
        
        return np.format_float_positional(d, precision=2), corners[distance==d].ravel()
    except:
        return 'Cannot determine', []

def get_distance_from_horizontal_lines( vline, line_params_chip, X, labels, good_labels):
    """ Calculate distance using left most points on the obtained horizontal lines """

    slope = line_params_chip[0]
    intercept = line_params_chip[1]

    try:

        ycoord = []
        xcoord = []
        for j in good_labels:
            coord = X[labels==j]
            argminima = np.argmin(coord,0)
            ycoord.append(coord[argminima[0]][1])
            xcoord.append(coord[argminima[0]][0]+vline)

        distance = []
        for x, y in zip(xcoord, ycoord):
            distance.append(abs(-x +slope*y + intercept) / math.sqrt(slope*slope + 1) )

        d = min(distance)

        xcoord = np.array(xcoord)
        ycoord = np.array(ycoord)
        coord = [xcoord[distance == d], ycoord[distance == d]]

        return np.format_float_positional(d, precision=2), coord
    except:
        return 'Cannot determine', []

### Check user's inputs if they satisfy the requirements
def variable_checking(text, typ_func, rng):
    try:
        value = typ_func(text)
        if (value-rng[0])*(value-rng[1]) < 0:
            return True
        else:
            return False
    except:
        return False

### Main function to yield processed image
def get_processed_array(img, vline, upper_hline, lower_hline, cluster_n_components, edge, threshold, quality=0.1):
    ### Step 1: Gray conversion + Smoothening
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (0,0), 2)

    ### Step 2: Image separation and processing
    img_left, img_right = img_separator(blur, vline=vline)
    
    ### Chip img processing
    if edge[0]:
        contour_chip = auto_canny(img_left, threshold[0]) ## threshold is the sigma value from 0 to 100%
        cannychip = threshold[0]
    else:
        contour_chip = auto_canny(img_left)
        cannychip = 0.33     
    
    angled_line_chip, line_params_chip, _, _, _ = get_axial_line(contour_chip, True, 'last', 20, cluster_n_components[0])
    
    ### Fiber img processing
    if background_profiler(img_right) >= 150:
        contrast_enhanced_fiber = contrast_enhancer(img_right)
    else:
        contrast_enhanced_fiber = img_right.copy()
    
    if edge[1]:
        binary_fiber = binary_threshold(contrast_enhanced_fiber, threshold[1])
        otsufiber = threshold[1]
    else:
        otsufiber, binary_fiber = adapt_thresh_otsu(contrast_enhanced_fiber)
        
    contour_fiber = get_contours(binary_fiber, False)
    angled_line_fiber, line_params_fiber, X, labels, good_labels  = get_axial_line(contour_fiber[upper_hline:lower_hline,:], 
        False, 'all', 20, cluster_n_components[1])
    
    ### Step 3: Calculate angle alpha 1 (between chip edge and vline) and alpha 2 (between chip edge and fiber axis)
    ### Alpha 1
    alpha1 = get_angle(line_params_chip[0], np.inf)
    alpha2 = get_angle(line_params_chip[0], line_params_fiber[0])
    """
    if (line_params_chip[0] is None) | (line_params_fiber[0] is None):
        chip_fiber_angle = 'Cannot determine angle'
    else:
        chip_fiber_angle = 'Angle: ' + get_angle(line_params_chip[0], line_params_fiber[0])
    """

    ### Step 4: Detect corners and calculate vertical distance (to chip edge)
    distancecorner, corners = get_distance(img_right[upper_hline:lower_hline,:], vline, line_params_chip, quality)
    distanceline, coord = get_distance_from_horizontal_lines(vline, line_params_chip, X, labels, good_labels)

    ### Step 5: Join image and return angle value
    processed = img_join(angled_line_chip[upper_hline:lower_hline,:], angled_line_fiber) # if we want to show angled line img
    # processed = img_join(contour_chip[lower_hline:upper_hline,:], contour_fiber[lower_hline:upper_hline,:]) # if we want to show only contour img
    processed = np.array(processed)
    ### Step 6: Draw distance
    thickness = 5
    if len(corners) > 0:
        rad = np.arctan(line_params_chip[0])
        #processed2 = processed.copy()
        processed2 = cv.line(processed, (int(corners[0]), int(corners[1])), 
            ( int(corners[0]-np.cos(rad)*float(distancecorner) + thickness), int(corners[1]-np.sin(rad)*float(distancecorner) + thickness) ),
                (230, 216, 173), thickness=thickness, lineType=cv.LINE_AA) ### Light blue
    else:
        processed2 = processed.copy()

    if len(coord) > 0:
        rad = np.arctan(line_params_chip[0])
        #processed2 = processed.copy()
        processed3 = cv.line(processed2, (int(coord[0]), int(coord[1])), 
            ( int(coord[0]-np.cos(rad)*float(distanceline) + thickness), int(coord[1]-np.sin(rad)*float(distanceline) + thickness) ),
                (0, 243, 255), thickness=thickness, lineType=cv.LINE_AA) ### Yellow
    else:
        processed3 = processed2.copy()

    height = lower_hline-upper_hline
    cropped = processed3[:,max(int(vline-height/2),0):min(int(vline+height/2),processed.shape[1])]
    return cropped, alpha1, alpha2, distancecorner, corners, distanceline, coord, cannychip, otsufiber, contour_chip, contour_fiber

