
from turtle import width
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2
from Example_mv01 import *
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        # self.setGeometry(0,0,4000,2000)
        self.setWindowTitle("GUI")
        self.initUI()

    def initUI(self):
        ### Variable for horizontal pixel
        self.line = 1000

        ### FONT VARIABLE
        self.fontvar = QFont('Times', 16)
        self.fontvar.setBold(True)

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
        # MOSFET IMAGE
        pixmapimage = QPixmap('Photos/Photo_Fiber_Obj_20X.tif')
        pixmapimage = pixmapimage.scaled(int(700/3240*width), int(700/2160*height), Qt.KeepAspectRatio)
        self.labelimage = QLabel(self)
        self.labelimage.setPixmap(pixmapimage)
        self.labelimage.setGeometry(int(20/3240*width),int(200/2160*height),int(700/3240*width),int(700/2160*height))



        ### PROCESSED IMAGE gets drawn by painter 

        img = get_array('Photos/Photo_Fiber_Obj_20X.tif')
	### Processed array now will include contour (to compatible with adaptive threshold, which not require contour)
        processed_array = get_processed_array(img) 
        # cv2.imwrite('Photos/Processed_10X.jpg', processed_array)

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
        self.bup.setText("+")
        self.bup.clicked.connect(self.clickdown)
        self.bup.setMaximumSize(int(120/3240*width),int(40/2160*height))
        # self.bup.move(1600,430)

        self.bdown = QPushButton(self)
        self.bdown.setText("-")
        self.bdown.clicked.connect(self.clickup)
        self.bdown.setMaximumSize(int(120/3240*width),int(40/2160*height))
        # self.bdown.move(1600,550)

        self.textline = QLineEdit()
        self.textline.textChanged.connect(self.textchanged)
        self.textline.setMaximumSize(int(120/3240*width),int(40/2160*height))
        self.textline.setGeometry(int(1600/3240*width),int(490/2160*height),int(120/3240*width),int(40/2160*height))


        """ 
        PLOT
        """
        # Initialize Axes
        self.insert_ax()

        # Get the picture information and store
        array = get_array('Photos/Photo_Fiber_Obj_20X.tif')
        self.processed = get_processed_array(array)
        self.blank = get_contours_array(self.processed)
        self.peaks = get_peaks(self.blank, self.line)
        
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

        hbox = QHBoxLayout()
        hbox.addSpacing(int(600/3240*width))
        hbox.addLayout(vboxbuttons)

        vbox = QVBoxLayout()
        # vbox.addSpacing(1000)
        vbox.addSpacing(int(420/2160*height))
        vbox.addLayout(hbox)
        vbox.addSpacing(int(420/2160*height))
        vbox.addWidget(self.canvas)
        
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(vbox)
        self.setCentralWidget(self.centralWidget)

    """
    LINE ON IMAGE
    """
    def paintEvent(self, event):
        painter = QPainter(self)
        self.pixmapprocessed = QPixmap('Photos/Processed_10X.jpg')
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
        self.ax.set_ylabel('grayscale intensity')
        self.ax.set_xlabel('pixel')
        self.ax.set_ylim([-5,260])
        self.graph, self.graphx = None, None

    def plot(self):
        array = get_array('Photos/Photo_Fiber_Obj_20X.tif')
        processed = get_processed_array(array)
        # blank = get_contours_array(processed)
        peaks = get_peaks(processed, self.line)

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)

        # Maybe change to ax as input var for function?
        self.ax = self.figure.add_subplot(111)
        self.graph = self.ax.plot(peaks, processed[self.line,:][peaks], "x", c="red")
        self.graphx = self.ax.plot(range(0,processed.shape[1]), processed[self.line,:])
        self.ax.set_title('Profiling of grayscale along the line')
        self.ax.set_ylabel('grayscale intensity')
        self.ax.set_xlabel('pixel')
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
            

    def updateplot(self):
        value = self.line
        processed = self.processed
        peaks = self.peaks
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