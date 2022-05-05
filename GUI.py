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



class MyWindow(QMainWindow):
    

    def __init__(self):
        super(MyWindow, self).__init__()
        # self.setGeometry(0,0,4000,2000)
        self.setWindowTitle("GUI")
        self.newimage = False
        self.folderAlreadySelected = False
        self.initUI()


    def initUI(self):
        
        if not self.folderAlreadySelected:
            self.setUpFolder()


        ### Variable for horizontal pixel
        self.topline = 200 # between 0 and 800
        self.botline = 400
        self.midline = 350

        ### Variable for binary, threshold, cluster and quality factor
        self.binary = [False, False]
        self.threshold = [63, 135]
        self.nb_cluster_components = [5,5]
        self.quality = 0.2

        # Initialize cropped and processed flags 
        self.drawCropped = False
        self.drawProcessed = False

        ### FONT VARIABLE
        self.fontvar = QFont('Times', 16)
        self.fontvar.setBold(True)


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
        self.textimage.setText("Crop Image")
        self.textimage.setFont(self.fontvar)
        self.textimage.setGeometry(int(1450/3240*width),int(50/2160*height), int(1000/3240*width),int(100/2160*height))

        self.textimage = QLabel(self)
        self.textimage.setText("Processed Image")
        self.textimage.setFont(self.fontvar)
        self.textimage.setGeometry(int(2500/3240*width),int(50/2160*height), int(1000/3240*width),int(100/2160*height))

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

        img = get_array(self.img_dir)
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
        # LABELS
        self.images = QLabel(self)
        self.images.setFixedHeight(int(3/5*height))
        
        self.chip = QLabel("Chip",self)
        self.fiber = QLabel("Fiber",self)
        
        self.thresh = QLabel("Binary threshold (< 250): ",self)
        self.clust = QLabel("Angle detection: ",self)
        self.cordet = QLabel("Corner detection (< 1): ",self)
        
        self.alpha1label = QLabel("Angle between chip and vertical axis: ",self)
        self.alpha2label = QLabel("Angle between fiber and horizontal axis: ",self)
        self.tethalabel = QLabel("Distance between chip and fiber: ",self)
        self.dlinelabel = QLabel("Distance between chip and fiber using horizontal line: ",self)
      
        self.alpha1value = QLabel(self)
        self.alpha2value = QLabel(self)
        self.tethavalue = QLabel(self)
        self.dlinevalue = QLabel(self)

        # INPUT TEXT
        self.cornerf = QLineEdit(self)
        self.cornerf.textChanged.connect(self.qualitycorner)
        self.cornerf.setMaximumWidth(100)

        self.chipvalue = QLineEdit(self)
        self.chipvalue.textChanged.connect(self.clusterchip)
        self.chipvalue.setMaximumWidth(100)

        self.fibervalue = QLineEdit(self)
        self.fibervalue.textChanged.connect(self.clusterfiber)
        self.fibervalue.setMaximumWidth(100)

        self.contourc = QLineEdit(self)
        self.contourc.textChanged.connect(self.binarychip)
        self.contourc.setMaximumWidth(100)

        self.contourf = QLineEdit(self)
        self.contourf.textChanged.connect(self.binaryfiber)
        self.contourf.setMaximumWidth(100)
        
        # BUTTONS
        
        self.bleft = QPushButton(self)
        self.bleft.setText("Left")
        self.bleft.clicked.connect(self.clickleft)
        self.bleft.setMaximumSize(int(180/3240*width),int(80/2160*height))
        # self.bup.move(1600,430)

        self.bright = QPushButton(self)
        self.bright.setText("Right")
        self.bright.clicked.connect(self.clickright)
        self.bright.setMaximumSize(int(180/3240*width),int(80/2160*height))

        self.textline = QLineEdit()
        self.textline.textChanged.connect(self.textchanged)
        self.textline.setMaximumSize(int(120/3240*width),int(40/2160*height))
        self.textline.setGeometry(int(1600/3240*width),int(490/2160*height),int(120/3240*width),int(40/2160*height))

        self.bnext = QPushButton(self)
        self.bnext.setText("Next Image")
        self.bnext.clicked.connect(self.clicknext)
        self.bnext.setMaximumSize(int(180/3240*width),int(80/2160*height))
        self.bnext.setGeometry(int(2900/3240*width),int(100/2160*height),int(120/3240*width),int(40/2160*height))

        self.textparameter = QLineEdit()
        self.textparameter.textChanged.connect(self.textchanged)
        self.textparameter.setMaximumSize(int(120/3240*width),int(40/2160*height))
        self.textparameter.setGeometry(int(2000/3240*width),int(490/2160*height),int(120/3240*width),int(40/2160*height))

        self.bbrowse = QPushButton(self)
        self.bbrowse.setText("Select")
        self.bbrowse.clicked.connect(self.browse)
        self.bbrowse.setMaximumSize(int(180/3240*width),int(80/2160*height))

        """
        LAY OUT
        """
        # Creating a grid of 4x8: first row is half of the windows, then buttons, 
        # texts and input parameters are in an specific position
        
        layout = QGridLayout()
        
        layout.addWidget(self.images, 0, 0, 1, 8) ## label covering half of window
        
        layout.addWidget(self.bnext, 1, 0)
        layout.setRowStretch(1,2)
        layout.addWidget(self.bbrowse ,1,1)

        ## Button
        layout.addWidget(self.bleft, 3, 0)
        layout.addWidget(self.bright, 4, 0)
        layout.addWidget(self.bcrop, 3, 1)
        layout.addWidget(self.bprocess, 4, 1)   

        ## Text labels
        layout.addWidget(self.thresh, 2, 3)
        layout.addWidget(self.clust, 3, 3)
        layout.addWidget(self.cordet, 4, 3)
        
        ## Text titles
        layout.addWidget(self.chip, 1, 4)
        layout.addWidget(self.fiber, 1, 5)
        
        ## Input parameters
        layout.addWidget(self.contourc, 2, 4)
        layout.addWidget(self.contourf, 2, 5)
        layout.addWidget(self.chipvalue, 3, 4)
        layout.addWidget(self.fibervalue, 3, 5)
        layout.addWidget(self.cornerf, 4, 5)

        ## Results
        layout.addWidget(self.alpha1label, 1, 7)
        layout.addWidget(self.alpha2label, 2, 7)
        layout.addWidget(self.tethalabel, 3, 7)
        layout.addWidget(self.dlinelabel, 4, 7)

        layout.addWidget(self.alpha1value, 1, 8)
        layout.addWidget(self.alpha2value, 2, 8)
        layout.addWidget(self.tethavalue, 3, 8)
        layout.addWidget(self.dlinevalue, 4, 8)
            
        layout.setRowStretch(5,2) ## for some reason, the first row goes up
        self.centralWidget = QWidget() 
        self.centralWidget.setLayout(layout)
        self.setCentralWidget(self.centralWidget)

        ''' 
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
        '''
    """
    LINE ON IMAGE
    """
    def paintEvent(self, event):
        painter = QPainter(self)

        """ Camera image """
        self.pixmapcameraimage = QPixmap(self.img_dir)
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
            img = get_array(self.img_dir)
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
            painter.drawPixmap(int(1200/3240*width),int(200/2160*height),int(800/3240*width),int(800/2160*height), self.pixmapcroppedimage)
            
            # Return draw cropped flag to False: remove otherwise plot disappear
            # self.drawCropped = False 

        """ Processed image drawing with painter """
        if self.drawProcessed:
            img = get_array(self.img_dir)
            size = img.shape
            # Convert gui scale to pixel value in array
            pxlmidline = int(self.midline/800*size[1])
            pxltopline = int(self.topline/800*size[0])
            pxlbotline = int(self.botline/800*size[0])

            processed_image = get_processed_array(img, pxlmidline, pxltopline, pxlbotline, self.nb_cluster_components, self.binary, self.threshold, self.quality)

            # Save image
            cv.imwrite('Photos/Processed/Processed.jpg', processed_image[0])

            # Show image
            self.pixmapprocessedimage = QPixmap('Photos/Processed/Processed.jpg')
            self.pixmapprocessedimage = self.pixmapprocessedimage.scaled(int(800/3240*width), int(800/2160*height), Qt.KeepAspectRatio)
            painter.drawPixmap(int(2200/3240*width),int(200/2160*height),int(800/3240*width),int(800/2160*height), self.pixmapprocessedimage)
            
            # Return draw processed flag to False
            self.drawProcessed = False

            # Print values
            self.alpha1value.setText(str(processed_image[1]) + " " + u"\u00b0")
            self.alpha2value.setText(str(processed_image[2]) + " " + u"\u00b0")
            self.tethavalue.setText(str(processed_image[3]) + " " + "pixels")
            self.dlinevalue.setText(str(int(processed_image[5]*100)/100) + " " + "pixels")
            


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

        
    def clickleft(self):
        """ One pixel up """
        self.line += 1
        self.updateplot()
        self.update() # painter update

    def clickright(self):
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

    def clusterchip(self, text):
        if text == "" or not isinstance(int(text),int):
            print('not a valid value')
            self.nb_cluster_components[0] = 5
        else: 
            self.nb_cluster_components[0] = int(text)
            
    def clusterfiber(self, text):
        if text == "" or not isinstance(int(text),int):
            print('not a valid value')
            self.nb_cluster_components[1] = 5
        else: 
            self.nb_cluster_components[1] = int(text)

    def binarychip(self, text):
        if text == "" or not isinstance(int(text),int):
            print('not an integer')
            self.binary[0] = False
            self.threshold[0] = 63
        else: 
            self.binary[0] = True
            self.threshold[0] = int(text)

    def binaryfiber(self, text):
        if text == "" or not isinstance(int(text),int):
            print('not an integer')
            self.binary[1] = False
            self.threshold[1] = 135
        else: 
            self.binary[1] = True
            self.threshold[1] = int(text)

    def qualitycorner(self, text):
        if text == "" or not isinstance(float(text),float):
            print('not a valid value')
            self.quality = 0.2
        else: 
            self.quality = float(text)
            
    def clicknext(self):
        """ One picture next """

        self.nb_pic += 1
        if self.nb_pic == len(self.photos):
            self.nb_pic = 0
        
        self.img_dir = self.directory + self.photos[self.nb_pic]
        self.newimage = True
        self.initUI()

    def browse(self):
        """ browse in directories to select photos folder """
        
        filename = QFileDialog.getExistingDirectory()
        self.directory = filename + '/'

        self.photos = os.listdir(self.directory)
        print(self.photos)

        i=0
        while i < len(self.photos):
            if self.photos[i]==".DS_Store" or self.photos[i] == "Processed":
                del self.photos[i] # Delete all invisible files like /.DS_Store
            else:
                i +=1

        ### Img directory
        self.nb_pic = 0
        self.img_dir = 'Photos/' + self.photos[self.nb_pic]
        self.folderAlreadySelected = True

    def setUpFolder(self):
        self.directory = 'Photos/'
        self.photos = os.listdir(self.directory)
        print(self.photos)

        i=0
        while i < len(self.photos):
            if self.photos[i]==".DS_Store" or self.photos[i] == "Processed":
                del self.photos[i] # Delete all invisible files like /.DS_Store
            else:
                i +=1

        ### Img directory
        self.nb_pic = 0
        self.img_dir = 'Photos/' + self.photos[self.nb_pic]
        self.folderAlreadySelected = True

        
            


      

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Standardize pixel positions using monitor resolution
    screen_rect = app.desktop().screenGeometry()
    width, height = screen_rect.width(), screen_rect.height()

    win = MyWindow()
    win.showMaximized()

    win.show()
    while True:
        sys.exit(app.exec_())