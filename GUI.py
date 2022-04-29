
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

directory = 'Photos/'
photos = os.listdir(directory)

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
        self.line = 1000

        ### FONT VARIABLE
        self.fontvar = QFont('Times', 16)
        self.fontvar.setBold(True)
        print('again', img_dir,nb_pic)

        """
        TEXT
        """
        self.textimage = QLabel(self)
        self.textimage.setText("Camera Image")
        self.textimage.setFont(self.fontvar)
        self.textimage.setGeometry(int(200/3240*width),int(50/2160*height), int(1000/3240*width),int(100/2160*height))

        self.textimage = QLabel(self)
        self.textimage.setText("Processed Image")
        self.textimage.setFont(self.fontvar)
        self.textimage.setGeometry(int(960/3240*width),int(50/2160*height), int(1000/3240*width),int(100/2160*height))

        self.textimage = QLabel(self)
        self.textimage.setText("Pixel Value on Intersection")
        self.textimage.setFont(self.fontvar)
        self.textimage.setGeometry(int(50/3240*width),int(920/2160*height), int(1000/3240*width),int(100/2160*height))
        
        """
        IMAGES
        """
        print(img_dir)
        # if self.newimage:
            # self.labelimage.clear()
        # CHIP FIBER IMAGE
        pixmapimage = QPixmap(img_dir)
        pixmapimage = pixmapimage.scaled(int(700/3240*width), int(700/2160*height), Qt.KeepAspectRatio)
        if not self.newimage:
            self.labelimage = QLabel(self)
        self.labelimage.setPixmap(pixmapimage)
        self.labelimage.setGeometry(int(20/3240*width),int(200/2160*height),int(700/3240*width),int(700/2160*height))



        ### PROCESSED IMAGE

        img = get_array(img_dir)

        self.processed = get_processed_array(img)
        cv.imwrite('Photos/Processed/Processed.jpg', self.processed)

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
        self.bup.setText("Up")
        self.bup.clicked.connect(self.clickdown)
        self.bup.setMaximumSize(int(120/3240*width),int(40/2160*height))
        # self.bup.move(1600,430)

        self.bdown = QPushButton(self)
        self.bdown.setText("Down")
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


        """ 
        PLOT
        """
        # Initialize Axes
        self.insert_ax()
        
        # Max value for self.line 
        self.maxyvalue = self.processed.shape[0]
        
        # Define First rectangle for green bar
        self.greenbar = QRect(int(780/3240*width),int((200+(self.line/self.maxyvalue*700))/2160*height-2),int(740/3240*width),5)

        # Update the graph
        self.updateplot()


        """
        LAY OUT
        """
        vboxbuttons = QVBoxLayout()
        vboxbuttons.addWidget(self.bup)
        vboxbuttons.addWidget(self.textline)
        vboxbuttons.addWidget(self.bdown)
        vboxbuttons.addWidget(self.bnext)

        hbox = QHBoxLayout()
        hbox.addSpacing(int(600/3240*width))
        hbox.addLayout(vboxbuttons)

        vbox = QVBoxLayout()
        # vbox.addSpacing(1000)
        vbox.addSpacing(int(420/2160*height))
        vbox.addLayout(hbox)
        vbox.addSpacing(int(420/2160*height))
        vbox.addWidget(self.canvasScale)
        
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(vbox)
        self.setCentralWidget(self.centralWidget)


    """
    LINE ON IMAGE
    """
    def paintEvent(self, event):
        painter = QPainter(self)
        self.pixmapprocessed = QPixmap('Photos/Processed/Processed.jpg')
        self.labelprocessed = QLabel(self)
        self.pixmapprocessed = self.pixmapprocessed.scaled(int(700/3240*width),int(700/2160*height),Qt.KeepAspectRatio)
        # self.labelprocessed.setPixmap(pixmapprocessed)
        painter.drawPixmap(int(800/3240*width),int(200/2160*height),int(700/3240*width),int(700/2160*height), self.pixmapprocessed)
        painter.setPen(QPen(Qt.green, 5, Qt.SolidLine))
        painter.drawLine(int(780/3240*width),int((200+(self.line/self.maxyvalue*700))/2160*height),int(1520/3240*width),int((200+(self.line/self.maxyvalue*700))/2160*height))

    def mousePressEvent(self,event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.lastPoint = event.pos()
    
    def mouseMoveEvent(self, event):
        if self.dragging and self.greenbar.contains(self.lastPoint):
            self.line = int( ((event.pos().y()/height*2160)-200)/700*self.maxyvalue )
            self.update()
            self.greenbar = QRect(int(780/3240*width),int((200+(self.line/self.maxyvalue*700))/2160*height-2),int(740/3240*width),5)
            self.lastPoint = event.pos()
            self.updateplot()

    def mouseReleaseEvent(self, event):
        if event.button == Qt.LeftButton:
            self.dragging = False



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