from logging import PlaceHolder
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
        self.fontvar = QFont('Times', 18)
        self.fontvar.setBold(True)

        ### FONT FOR CONTENT
        self.fontcontent = QFont('Times', 13)
        self.boxtitles = QFont('Times', 16)

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
        self.textimage.setText("Zoom Image")
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
        self.bcrop.setText("Show zoom image")
        self.bcrop.setFont(self.fontcontent)
        self.bcrop.clicked.connect(self.get_cropped)
        self.bcrop.setMaximumSize(int(400/3240*width),int(80/2160*height))

        self.bprocess = QPushButton(self)
        self.bprocess.setText("Show processed image")
        self.bprocess.setFont(self.fontcontent)
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
        self.chip.setFont(self.fontcontent)
        self.fiber = QLabel("Fiber",self)
        self.fiber.setFont(self.fontcontent)
        self.foldertext = QLabel("In directory: visionautomation/"+self.directory,self)
        self.foldertext.setFont(self.fontcontent)

        self.thresh = QLabel("Binary threshold: ",self)
        self.thresh.setFont(self.fontcontent)
        self.clust = QLabel("Angle detection: ",self)
        self.clust.setFont(self.fontcontent)
        self.cordet = QLabel("Corner detection: ",self)
        self.cordet.setFont(self.fontcontent)

        self.alpha1label = QLabel("Angle between chip and vertical axis: ",self)
        self.alpha1label.setFont(self.fontcontent)
        self.alpha2label = QLabel("Angle between fiber and chip edge: ",self)
        self.alpha2label.setFont(self.fontcontent)
        self.tethalabel = QLabel("Distance between chip and fiber (Corner detection): ",self)
        self.tethalabel.setFont(self.fontcontent)
        self.dlinelabel = QLabel("Distance between chip and fiber (Line detection): ",self)
        self.dlinelabel.setFont(self.fontcontent)

        self.alpha1value = QLabel(self)
        self.alpha1value.setStyleSheet("background-color:lightgreen; font-size: 14pt")
        self.alpha2value = QLabel(self)
        self.alpha2value.setStyleSheet("background-color:red; font-size: 14pt")
        self.tethavalue = QLabel(self)
        self.tethavalue.setStyleSheet("background-color:#ADD8E6; font-size: 14pt") #lightblue
        self.dlinevalue = QLabel(self)
        self.dlinevalue.setStyleSheet("background-color:yellow; font-size: 14pt")


        # INPUT TEXT
        self.cornerf = QLineEdit(placeholderText = str(self.quality))
        self.cornerf.textChanged.connect(self.qualitycorner)
        self.cornerf.setMaximumWidth(100)

        self.cornerf = QSlider()
        self.cornerf.setOrientation(Qt.Horizontal)
        self.cornerf.setTickPosition(QSlider.TicksBelow)
        self.cornerf.setTickInterval(1)
        self.cornerf.setMinimum(0)
        self.cornerf.setMaximum(100)
        self.cornerf.setValue(int(self.quality*100))
        self.cornerf.setMaximumSize(int(200/3240*width),int(30/2160*height))
        self.cornerf.valueChanged.connect(self.valueCornerDetection)

        self.chipvalue = QLineEdit(placeholderText = str(self.nb_cluster_components[0]))
        self.chipvalue.textChanged.connect(self.clusterchip)
        self.chipvalue.setMaximumWidth(100)

        self.chipvalue = QSlider()
        self.chipvalue.setOrientation(Qt.Horizontal)
        self.chipvalue.setTickPosition(QSlider.TicksBelow)
        self.chipvalue.setTickInterval(1)
        self.chipvalue.setMinimum(1)
        self.chipvalue.setMaximum(100)
        self.chipvalue.setValue(self.nb_cluster_components[0]*10)
        self.chipvalue.setMaximumSize(int(200/3240*width),int(30/2160*height))
        self.chipvalue.valueChanged.connect(self.valueChipCluster)

        self.fibervalue = QLineEdit(placeholderText = str(self.nb_cluster_components[1]))
        self.fibervalue.textChanged.connect(self.clusterfiber)
        self.fibervalue.setMaximumWidth(100)

        self.fibervalue = QSlider()
        self.fibervalue.setOrientation(Qt.Horizontal)
        self.fibervalue.setTickPosition(QSlider.TicksBelow)
        self.fibervalue.setTickInterval(1)
        self.fibervalue.setMinimum(1)
        self.fibervalue.setMaximum(100)
        self.fibervalue.setValue(self.nb_cluster_components[1]*10)
        self.fibervalue.setMaximumSize(int(200/3240*width),int(30/2160*height))
        self.fibervalue.valueChanged.connect(self.valueFiberCluster)

        self.contourc = QLineEdit(placeholderText = "...")
        self.contourc.textChanged.connect(self.binarychip)
        self.contourc.setMaximumWidth(100)

        self.contourc = QSlider()
        self.contourc.setOrientation(Qt.Horizontal)
        self.contourc.setTickPosition(QSlider.TicksBelow)
        self.contourc.setTickInterval(1)
        self.contourc.setMinimum(1)
        self.contourc.setMaximum(250)
        self.contourc.setValue(1)
        self.contourc.setMaximumSize(int(200/3240*width),int(30/2160*height))
        self.contourc.valueChanged.connect(self.valueChipContour)

        self.contourf = QLineEdit(placeholderText = "...")
        self.contourf.textChanged.connect(self.binaryfiber)
        self.contourf.setMaximumWidth(100)

        self.contourf = QSlider()
        self.contourf.setOrientation(Qt.Horizontal)
        self.contourf.setTickPosition(QSlider.TicksBelow)
        self.contourf.setTickInterval(1)
        self.contourf.setMinimum(1)
        self.contourf.setMaximum(250)
        self.contourf.setValue(1)
        self.contourf.setMaximumSize(int(200/3240*width),int(30/2160*height))
        self.contourf.valueChanged.connect(self.valueFiberContour)
        
        # BUTTONS
        self.bleft = QPushButton(self)
        self.bleft.setText("Left")
        self.bleft.setFont(self.fontcontent)
        self.bleft.clicked.connect(self.clickleft)
        self.bleft.setMaximumSize(int(400/3240*width),int(100/2160*height))
        # self.bup.move(1600,430)

        self.bright = QPushButton(self)
        self.bright.setText("Right")
        self.bright.setFont(self.fontcontent)
        self.bright.clicked.connect(self.clickright)
        self.bright.setMaximumSize(int(400/3240*width),int(100/2160*height))

        self.textline = QLineEdit()
        self.textline.textChanged.connect(self.textchanged)
        self.textline.setMaximumSize(int(120/3240*width),int(40/2160*height))
        self.textline.setGeometry(int(1600/3240*width),int(490/2160*height),int(120/3240*width),int(40/2160*height))

        self.bnext = QPushButton(self)
        self.bnext.setText("Next Image")
        self.bnext.setFont(self.fontcontent)
        self.bnext.clicked.connect(self.clicknext)
        self.bnext.setMaximumSize(int(400/3240*width),int(100/2160*height))
        self.bnext.setGeometry(int(2900/3240*width),int(100/2160*height),int(120/3240*width),int(40/2160*height))

        self.textparameter = QLineEdit()
        self.textparameter.textChanged.connect(self.textchanged)
        self.textparameter.setMaximumSize(int(120/3240*width),int(40/2160*height))
        self.textparameter.setGeometry(int(2000/3240*width),int(490/2160*height),int(120/3240*width),int(40/2160*height))

        self.bbrowse = QPushButton(self)
        self.bbrowse.setText("Select")
        self.bbrowse.setFont(self.fontcontent)
        self.bbrowse.clicked.connect(self.browse)
        self.bbrowse.setMaximumSize(int(400/3240*width),int(100/2160*height))

        """
        LAY OUT
        """
        # Creating a grid for grid boxes, outer grid 2X3: first row is half of the windows, second row are the 3 grid boxes
        # Boxes are: 1 for buttons, 1 for input parameters and 1 for results, each of them are define as grids
        
        layout = QGridLayout()
        butlayout = QGridLayout()
        inputslayout = QGridLayout()
        resultslayout = QGridLayout()

        boxofbuttons = QGroupBox(str("Control Pannel"))
        boxofbuttons.setFont(self.boxtitles)
        boxofbuttons.setFixedSize(int(1/4*width),int(1/5*height))
        boxofinputs = QGroupBox(str("Adjustable parameters"))
        boxofinputs.setFont(self.boxtitles)
        boxofresults = QGroupBox(str("Results"))
        boxofresults.setFont(self.boxtitles)
        boxofresults.setFixedSize(int(1/3*width),int(1/5*height))

        layout.addWidget(self.images, 0, 0, 1, 3) ## label covering half of window

        ## Buttons
        layout.addWidget(boxofbuttons,1,1)
        butlayout.addWidget(self.foldertext, 0,0,1,2)
        butlayout.addWidget(self.bnext, 1, 0)
        #butlayout.setRowStretch(1,2)
        butlayout.addWidget(self.bbrowse ,1,1)
        butlayout.addWidget(self.bleft, 3, 0)
        butlayout.addWidget(self.bright, 3, 1)
        butlayout.addWidget(self.bcrop, 4, 0)
        butlayout.addWidget(self.bprocess, 4, 1)
        boxofbuttons.setLayout(butlayout)

        ## Process
        layout.addWidget(boxofinputs,1,3)
        # Text labels
        inputslayout.addWidget(self.thresh, 2, 3)
        inputslayout.addWidget(self.clust, 3, 3)
        inputslayout.addWidget(self.cordet, 4, 3)
        # Text titles
        inputslayout.addWidget(self.chip, 1, 4)
        inputslayout.addWidget(self.fiber, 1, 5)
        # Input parameters
        inputslayout.addWidget(self.contourc, 2, 4)
        inputslayout.addWidget(self.contourf, 2, 5)
        inputslayout.addWidget(self.chipvalue, 3, 4)
        inputslayout.addWidget(self.fibervalue, 3, 5)
        inputslayout.addWidget(self.cornerf, 4, 5)
        boxofinputs.setLayout(inputslayout)

        ## Results
        layout.addWidget(boxofresults,1,7)
        #Text labels
        resultslayout.addWidget(self.alpha1label, 1, 7)
        resultslayout.addWidget(self.alpha2label, 2, 7)
        resultslayout.addWidget(self.tethalabel, 3, 7)
        resultslayout.addWidget(self.dlinelabel, 4, 7)
        #Output parameters
        resultslayout.addWidget(self.alpha1value, 1, 8)
        resultslayout.addWidget(self.alpha2value, 2, 8)
        resultslayout.addWidget(self.tethavalue, 3, 8)
        resultslayout.addWidget(self.dlinevalue, 4, 8)
        boxofresults.setLayout(resultslayout)

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

            # Get initial binary threshold values from otsu function:
            self.contourc.setValue(int(processed_image[7]))
            self.contourf.setValue(int(processed_image[8]))
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
            self.dlinevalue.setText(str(processed_image[5]) + " " + "pixels")
            


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

    def valueCornerDetection(self):
        value = self.cornerf.value()/100
        self.quality = value

    def valueChipContour(self):
        self.threshold[0] = int(self.contourc.value())
        self.binary[0] = True


    def valueFiberContour(self):
        self.threshold[1] = int(self.contourf.value())
        self.binary[1] = True
 
    def valueChipCluster(self):
        value = self.chipvalue.value()/10
        self.nb_cluster_components[0] = int(value)
        print(self.nb_cluster_components)

    def valueFiberCluster(self):
        value = self.fibervalue.value()/10
        self.nb_cluster_components[1] = int(value)


    def get_cropped(self):
        """ Activate code to draw the cropped image in the top middle """
        self.drawCropped = True
        self.update() # painter update

    def get_processed(self):
        """ Activate code to draw the processed image with results in the top right """
        self.drawProcessed = True
        self.update() # painter update


        
    def clickleft(self):
        """ One pixel to left """
        self.midline -= 1
        self.update() # painter update

    def clickright(self):
        """ One pixel to right """
        self.midline += 1
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
        if variable_checking(text, int, [0,10]):
            self.nb_cluster_components[0] = int(text)
        else:
            print(text + ' is not a valid value')
            self.nb_cluster_components[0] = 5 
            
            
    def clusterfiber(self, text):
        if variable_checking(text, int, [0,10]):
            self.nb_cluster_components[1] = int(text)
        else:
            print(text + ' is not a valid value')
            self.nb_cluster_components[1] = 5 


    def binarychip(self, text):
        if variable_checking(text, int, [0, 251]):
            self.binary[0] = True
            self.threshold[0] = int(text)
        else:
            print(text + ' is not a valid value')
            self.binary[0] = False
            self.threshold[0] = 63
        

    def binaryfiber(self, text):
        if variable_checking(text, int, [0, 251]):
            self.binary[1] = True
            self.threshold[1] = int(text)
        else:
            print(text + ' is not a valid value')
            self.binary[1] = False
            self.threshold[1] = 135


    def qualitycorner(self, text):
        if variable_checking(text, float, [0, 1]):
            self.quality = float(text)
        else:
            print(text + ' is not a valid value')
            self.quality = 0.2


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