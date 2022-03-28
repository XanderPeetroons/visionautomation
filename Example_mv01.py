import cv2 as cv
import numpy as np

img = cv.imread('Photos/mosfet.jpg')
cv.imshow('Mosfet',img)

blank = np.zeros(img.shape[:2], dtype = 'uint8')
cv.imshow('Blank',blank)

#Converting to grayscale
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
cv.imshow('Gray', gray)

#Blur
#blur = cv.GaussianBlur(img, (7,7), cv.BORDER_DEFAULT)
#cv.imshow('Blur',blur)

#Edge cascades
canny = cv.Canny(img, 125, 125)
#canny = cv.Canny(blur, 125, 125)
cv.imshow('Canny edges', canny)

# Dilating the image
#dilated = cv.dilate(canny, (3,3), iterations=3)
#cv.imshow('Dilated', dilated)

ret, thresh = cv.threshold(gray,125,125, cv.THRESH_BINARY)
cv.imshow('Thresh',thresh)

contours, hierarchies = cv.findContours(canny, cv.RETR_LIST,cv.CHAIN_APPROX_NONE)
print(f'{len(contours)} contour(s) found!')

cv.drawContours(blank, contours, -1, (0,0,255), 2)
cv.imshow('Countors Drawn', blank)

cv.waitKey(0)

