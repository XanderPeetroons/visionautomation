
from turtle import width
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2 as cv
from img_processing import *
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import os
import time

directory = 'Photos/'
photos = os.listdir(directory)

i=0
while i < len(photos):
    if '.' in photos[i]:
        del photos[i] # Delete all invisible files like /.DS_Store
    i +=1

### Img directory
nb_pic = 0
img_dir = 'Photos/' + photos[nb_pic]


class MyWindow(QMainWindow):
    

    def __init__(self):
        super(MyWindow, self).__init__()
        # self.setGeometry(0,0,4000,2000)
        self.setWindowTitle("GUI")
        self.newimage = False
        self.initUI()


    def initUI(self):
        global img_dir

        ### Variable for horizontal pixel
        self.topline = 200 # between 0 and 800
        self.botline = 400
        self.midline = 350

        # Initialize cropped and processed flags 
        self.drawCropped = False
        self.drawProcessed = False

        ### FONT VARIABLE
        self.fontvar = QFont('Times', 16)
        self.fontvar.setBold(True)
        print('again', img_dir,nb_pic)


        """
        1: TOP LEFT: CAMERA IMAGE + AREA OF INTEREST
        """

        self.textimage = QLabel(self)
        self.textimage.setText("Camera Image")
        self.textimage.setFont(self.fontvar)
        self.textimage.setGeometry(int(300/3240*width),int(50/2160*height), int(1000/3240*width),int(100/2160*height))

        # Area of Interest bars
        self.hbartop = QRect(int(10/3240*width),int((200+self.topline)/2160*height-4),int(840/3240*width),9)
        self.hbarbot = QRect(int(10/3240*width),int((200+self.botline)/2160*height-4),int(840/3240*width),9)
        self.vbarmid = QRect(int((50+self.midline)/3240*width-4),int(180/2160*height),9,int(840/3240*width))

        # Image and lines are drawn in paintEvent()
        
        
        """
        2: TOP MIDDLE: CROPPED IMAGE TO AREA OF INTEREST
        """

        self.textimage = QLabel(self)
        self.textimage.setText("Processed Image")
        self.textimage.setFont(self.fontvar)
        self.textimage.setGeometry(int(960/3240*width),int(50/2160*height), int(1000/3240*width),int(100/2160*height))

        """
        4: BOT LEFT: BUTTONS FOR ACTIVATION
        """

        self.bcrop = QPushButton(self)
        self.bcrop.setText("Get cropped image")
        self.bcrop.clicked.connect(self.get_cropped)
        self.bcrop.setMaximumSize(int(400/3240*width),int(80/2160*height))

        self.bprocess = QPushButton(self)
        self.bprocess.setText("Get processed image")
        self.bprocess.clicked.connect(self.get_processed)
        self.bprocess.setMaximumSize(int(400/3240*width),int(80/2160*height))

        ### PROCESSED IMAGE gets drawn by painter 

        img = get_array(img_dir)
	    ### Processed array now will include contour
        # self.processed = get_processed_array(img) 
        # cv.imwrite('Photos/Processed_10X.jpg', processed_array)

        """ Read from array """
        # img = cv2.imread('2.jpg')
        # height, width, bytesPerComponent = img.shape
        # bytesPerLine = 3 * width
        # cv2.cvtColor(img, cv2.COLOR_BGR2RGB, img)
        # QImg = QImage(img.data, width, height, bytesPerLine,QImage.Format_RGB888)
        # pixmap = QPixmap.fromImage(QImg)

        # pixmapprocessed = QPixmap('Photos/Processed_10X.jpg')
        # self.labelprocessed = QLabel(self)
        # pixmapprocessed = pixmapprocessed.scaled(int(700/3240*width),int(700/2160*height),Qt.KeepAspectRatio)
        # # self.labelprocessed.setPixmap(pixmapprocessed)
        # self.labelprocessed.setGeometry(int(800/3240*width),int(200/2160*height),int(700/3240*width),int(700/2160*height))


        """
        TOOLS
        """
        # BUTTONS
        self.bup = QPushButton(self)
        self.bup.setText("up")
        self.bup.clicked.connect(self.clickdown)
        self.bup.setMaximumSize(int(120/3240*width),int(40/2160*height))
        # self.bup.move(1600,430)

        self.bdown = QPushButton(self)
        self.bdown.setText("down")
        self.bdown.clicked.connect(self.clickup)
        self.bdown.setMaximumSize(int(120/3240*width),int(40/2160*height))
        # self.bdown.move(1600,550)

        self.textline = QLineEdit()
        self.textline.textChanged.connect(self.textchanged)
        self.textline.setMaximumSize(int(120/3240*width),int(40/2160*height))
        self.textline.setGeometry(int(1600/3240*width),int(490/2160*height),int(120/3240*width),int(40/2160*height))

        self.bnext = QPushButton(self)
        self.bnext.setText("Next Image")
        self.bnext.clicked.connect(self.clicknext)
        self.bnext.setMaximumSize(int(120/3240*width),int(40/2160*height))
        self.bnext.setGeometry(int(2900/3240*width),int(100/2160*height),int(120/3240*width),int(40/2160*height))

        self.textparameter = QLineEdit()
        self.textparameter.textChanged.connect(self.textchanged)
        self.textparameter.setMaximumSize(int(120/3240*width),int(40/2160*height))
        self.textparameter.setGeometry(int(2000/3240*width),int(490/2160*height),int(120/3240*width),int(40/2160*height))

        """ 
        PLOT
        """
        # Initialize Axes
        # self.insert_ax()

        # Get the picture information and store
        
        # Max value for self.line 
        # self.maxyvalue = self.processed.shape[0]
        
        # Define First rectangle for green bar
        # self.greenbar = QRect(int(780/3240*width),int((200+(self.line/self.maxyvalue*700))/2160*height-2),int(740/3240*width),5)


        """
        LAY OUT
        """
        

        vboxbuttons = QVBoxLayout()
        vboxbuttons.addWidget(self.bcrop)
        vboxbuttons.addWidget(self.bprocess)

        hbox = QHBoxLayout()
        hbox.addLayout(vboxbuttons)
        hbox.addSpacing(int(2350/3240*width))


        vbox = QVBoxLayout()
        # vbox.addSpacing(1000)
        vbox.addSpacing(int(600/2160*height))
        vbox.addLayout(hbox)
        
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(vbox)
        self.setCentralWidget(self.centralWidget)

    """
    LINE ON IMAGE
    """
    def paintEvent(self, event):
        painter = QPainter(self)

        """ Camera image """
        self.pixmapcameraimage = QPixmap(img_dir)
        self.pixmapcameraimage = self.pixmapcameraimage.scaled(int(800/3240*width), int(800/2160*height), Qt.KeepAspectRatio)
        painter.drawPixmap(int(50/3240*width),int(200/2160*height),int(800/3240*width),int(800/2160*height), self.pixmapcameraimage)

        # Processed drawing with painter
        # self.pixmapprocessed = QPixmap('Photos/Processed/processed.jpg')
        # self.pixmapprocessed = convertCvImage2QtImage(self.processed)
        # self.labelprocessed = QLabel(self)
        # self.pixmapprocessed = self.pixmapprocessed.scaled(int(700/3240*width),int(700/2160*height),Qt.KeepAspectRatio)
        # self.labelprocessed.setPixmap(pixmapprocessed)
        # painter.drawPixmap(int(800/3240*width),int(200/2160*height),int(700/3240*width),int(700/2160*height), self.pixmapprocessed)
        
        """ Line drawings with painter """

        # Top line
        painter.setPen(QPen(Qt.white, 5, Qt.SolidLine))
        painter.drawLine(int(30/3240*width),int((200+self.topline)/2160*height),int(870/3240*width),int((200+self.topline)/2160*height))
        # Bottom line
        painter.drawLine(int(30/3240*width),int((200+self.botline)/2160*height),int(870/3240*width),int((200+self.botline)/2160*height))
        # Vertical line middle
        painter.drawLine(int((50+self.midline)/3240*width),int(180/2160*height),int((50+self.midline)/3240*width),int(1020/2160*height))

        """ Cropped image drawing with painter"""
        if self.drawCropped:
            img = get_array(img_dir)
            size = img.shape
            # Convert gui scale to pixel value in array
            pxlmidline = int(self.midline/800*size[1])
            pxltopline = int(self.topline/800*size[0])
            pxlbotline = int(self.botline/800*size[0])
            cropped_image = get_cropped_image(img, pxlmidline, pxltopline, pxlbotline)

            # Save image
            cv.imwrite('Photos/Processed/Cropped.jpg', cropped_image)

            self.pixmapcroppedimage = QPixmap('Photos/Processed/Cropped.jpg')
            self.pixmapcroppedimage = self.pixmapcroppedimage.scaled(int(800/3240*width), int(800/2160*height), Qt.KeepAspectRatio)
            painter.drawPixmap(int(1000/3240*width),int(200/2160*height),int(800/3240*width),int(800/2160*height), self.pixmapcroppedimage)
            
            # Return draw cropped flag to False
            self.drawCropped = False

        """ Processed image drawing with painter """
        if self.drawProcessed:
            img = get_array(img_dir)
            size = img.shape
            # Convert gui scale to pixel value in array
            pxlmidline = int(self.midline/800*size[1])
            pxltopline = int(self.topline/800*size[0])
            pxlbotline = int(self.botline/800*size[0])
            nb_cluster_components = [5,5]
            processed_image = get_processed_array(img, pxlmidline, pxltopline, pxlbotline, nb_cluster_components)

            # Save image
            cv.imwrite('Photos/Processed/Processed.jpg', processed_image[0])


            self.pixmapprocessedimage = QPixmap('Photos/Processed/Processed.jpg')
            self.pixmapprocessedimage = self.pixmapprocessedimage.scaled(int(800/3240*width), int(800/2160*height), Qt.KeepAspectRatio)
            painter.drawPixmap(int(2000/3240*width),int(200/2160*height),int(800/3240*width),int(800/2160*height), self.pixmapprocessedimage)
            
            # Return draw cropped flag to False
            self.drawProcessed = False


    def mousePressEvent(self,event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.lastPoint = event.pos()
    
    def mouseMoveEvent(self, event):
        if self.dragging and self.hbartop.contains(self.lastPoint):
            self.topline = int( ((event.pos().y()/height*2160)-200))
            self.update()
            self.hbartop = QRect(int(30/3240*width),int((200+self.topline)/2160*height-4),int(840/3240*width),9)
            self.lastPoint = event.pos()

        elif self.dragging and self.hbarbot.contains(self.lastPoint):
            self.botline = int( ((event.pos().y()/height*2160)-200))
            self.update()
            self.hbarbot = QRect(int(30/3240*width),int((200+self.botline)/2160*height-4),int(840/3240*width),9)
            self.lastPoint = event.pos()

        elif self.dragging and self.vbarmid.contains(self.lastPoint):
            self.midline = int( ((event.pos().x()/width*3240)-50))
            self.update()
            self.vbarmid = QRect(int((50+self.midline)/3240*width-4),int(180/2160*height),9,int(840/3240*width))
            self.lastPoint = event.pos()
            

    def mouseReleaseEvent(self, event):
        if event.button == Qt.LeftButton:
            self.dragging = False

    def get_cropped(self):
        """ Activate code to draw the cropped image in the top middle """
        self.drawCropped = True
        self.update() # painter update

    def get_processed(self):
        """ Activate code to draw the processed image with results in the top right """
        self.drawProcessed = True
        self.update() # painter update


    def insert_ax(self):
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)

        # Maybe change to ax as input var for function?
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title('Profiling of grayscale along the line')
        self.ax.set_ylabel('Grayscale intensity')
        self.ax.set_xlabel('Pixel')
        self.ax.set_ylim([-5,260])
        self.graph, self.graphx = None, None

    def plot(self):
        processed = self.processed
        peaks = get_peaks(processed, self.line)

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)

        # Maybe change to ax as input var for function?
        self.ax = self.figure.add_subplot(111)
        self.graph = self.ax.plot(peaks, processed[self.line,:][peaks], "x", c="red")
        self.graphx = self.ax.plot(range(0,processed.shape[1]), processed[self.line,:])
        self.ax.set_title('Profiling of grayscale along the line')
        self.ax.set_ylabel('Grayscale intensity')
        self.ax.set_xlabel('Pixel')
        self.ax.set_ylim([-5,260])
        self.canvas.resize(1000,1000) 

    def clickup(self):
        """ One pixel up """
        self.line += 1
        self.updateplot()
        self.update() # painter update

    def clickdown(self):
        """ One pixel down """
        self.line -= 1
        self.updateplot()
        self.update() # painter update

    def textchanged(self, text):
        """ Intersection to the input pixel """
        if text == "" or not isinstance(int(text),int):
            print('not an integer')
        else: 
            self.line = int(text)
            self.updateplot()
            self.update() # painter update

    def clicknext(self):
        """ One picture next """
        global nb_pic 
        global img_dir

        print('here')
        nb_pic += 1
        img_dir = 'Photos/' + photos[nb_pic]
        self.newimage = True
        self.initUI()
        
            

    def updateplot(self):
        value = self.line
        processed = self.processed
        peaks = get_peaks(processed, self.line)
        try: 
            value = float(value)
        except ValueError:
            value = 250

        # Renew graph
        if self.graphx:
            line = self.graph.pop(0)
            line.remove()
            line = self.graphx.pop(0)
            line.remove()
        
        self.graph = self.ax.plot(peaks, processed[self.line,:][peaks], "x", c="red")
        self.graphx = self.ax.plot(range(0,processed.shape[1]), processed[self.line,:])
        self.canvas.draw()

      

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Standardize pixel positions using monitor resolution
    screen_rect = app.desktop().screenGeometry()
    width, height = screen_rect.width(), screen_rect.height()
    print(width,height)

    win = MyWindow()
    win.showMaximized()

    win.show()
    while True:
        sys.exit(app.exec_())