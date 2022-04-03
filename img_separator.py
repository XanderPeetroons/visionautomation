### Import library
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy.signal import find_peaks
import math
import pwlf



def img_separator (img):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray,(5,5),5)

    x = np.arange(0,blur.shape[1])
    y = np.array(list(np.mean(blur[:,j]) for j in range(0,blur.shape[1])))
    
    my_pwlf = pwlf.PiecewiseLinFit(x, y)
    segment = my_pwlf.fit(3)
    mid = int((segment[1]+segment[2])/2)
    img_left = gray[:, :mid+50] # margin of 50 pixel
    img_right = gray[:, mid-50:]
    return img_left, img_right