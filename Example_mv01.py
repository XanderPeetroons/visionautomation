import cv2 as cv
from cv2 import THRESH_BINARY
import numpy as np
#import utlis

img = cv.imread('Photos/mosfet.jpg')
cv.imshow('Mosfet',img)

blank = np.zeros(img.shape[:2], dtype = 'uint8')
#cv.imshow('Blank',blank)

#Converting to grayscale
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
#cv.imshow('Gray', gray)

#Blur
#blur = cv.GaussianBlur(img, (7,7), cv.BORDER_DEFAULT)
#cv.imshow('Blur',blur)

#Edge cascades / only converts edge not interiors
#canny = cv.Canny(img, 125, 125)
#canny = cv.Canny(blur, 125, 125)
#cv.imshow('Canny edges', canny)

# Dilating the image
#dilated = cv.dilate(canny, (3,3), iterations=1)
#cv.imshow('Dilated', dilated)

#Erode
#erode = cv.erode(canny, np.ones((5,5)), iterations=5)
#cv.imshow('Erode', erode)

ret, thresh1 = cv.threshold(gray,130,255, cv.THRESH_BINARY)
#thresh2 = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,11,7)
cv.imshow('Thresh1',thresh1)
#cv.imshow('Thresh2',thresh2)

contours, hierarchies = cv.findContours(thresh1, cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)

#utlis.getContours(img,showCanny=True)



#contours, hierarchies = cv.findContours(thresh1, cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
#print(f'{len(contours)} contour(s) found!')

#cv.drawContours(blank, contours, -1, (255,255,255), 1)
#cv.imshow('Countors Drawn', blank)

cv.waitKey(0)