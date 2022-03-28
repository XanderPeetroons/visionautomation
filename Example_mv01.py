import cv2 as cv
from cv2 import THRESH_BINARY
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
import scipy
from scipy.signal import find_peaks
#import utlis


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

cv.waitKey(0)