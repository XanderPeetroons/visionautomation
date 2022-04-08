
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import cv2
from Example_mv01 import *
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(0,0,4000,2000)
        self.setWindowTitle("GUI")
        self.initUI()

    def initUI(self):
        # Variable for intersection pixel
        self.line = 250

        # FONT VARIABLE
        self.fontvar = QFont('Times', 16)
        self.fontvar.setBold(True)

        """
        TEXT
        """
        self.textimage = QLabel(self)
        self.textimage.setText("Camera Image")
        self.textimage.setFont(self.fontvar)
        self.textimage.setGeometry(200,50, 1000,100)

        self.textimage = QLabel(self)
        self.textimage.setText("Processed Image")
        self.textimage.setFont(self.fontvar)
        self.textimage.setGeometry(960,50, 1000,100)

        self.textimage = QLabel(self)
        self.textimage.setText("Pixel Value on Intersection")
        self.textimage.setFont(self.fontvar)
        self.textimage.setGeometry(50,920, 1000,100)
        
        """
        IMAGES
        """
        # MOSFET IMAGE
        pixmapimage = QPixmap('Photos/Photo_Fiber_Obj_10X.tif')
        pixmapimage = pixmapimage.scaled(700, 700, Qt.KeepAspectRatio)
        self.labelimage = QLabel(self)
        self.labelimage.setPixmap(pixmapimage)
        self.labelimage.setGeometry(20,200,700,700)

        # PROCESSED IMAGE
        # This code only once
        # img = get_array('Photos/Photo_Fiber_Obj_10X.tif')
        # processed_array = get_processed_array(img)
        # cv2.imwrite('Photos/Processed_10X.jpg', processed_array)

        pixmapprocessed = QPixmap('Photos/Processed_10X.jpg')
        self.labelprocessed = QLabel(self)
        pixmapprocessed = pixmapprocessed.scaled(700,700,Qt.KeepAspectRatio)
        self.labelprocessed.setPixmap(pixmapprocessed)
        self.labelprocessed.setGeometry(800,200,700,700)


        """
        TOOLS
        """
        # BUTTONS
        self.bup = QPushButton(self)
        self.bup.setText("+")
        self.bup.clicked.connect(self.clickup)
        self.bup.setMaximumSize(120,40)
        # self.bup.move(1600,430)

        self.bdown = QPushButton(self)
        self.bdown.setText("-")
        self.bdown.clicked.connect(self.clickdown)
        self.bdown.setMaximumSize(120,40)
        # self.bdown.move(1600,550)

        self.textline = QLineEdit()
        self.textline.textChanged.connect(self.textchanged)
        self.textline.setMaximumSize(120,40)
        self.textline.setGeometry(1600,490,120,40)


        """ 
        PLOT
        """
        # Initialize Axes
        self.insert_ax()

        # Get the picture information and store
        array = get_array('Photos/Photo_Fiber_Obj_10X.tif')
        processed = get_processed_array(array)
        self.blank = get_contours_array(processed)
        self.peaks = get_peaks(self.blank, self.line)
        
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
        hbox.addSpacing(1500)
        hbox.addLayout(vboxbuttons)

        vbox = QVBoxLayout()
        # vbox.addSpacing(1000)
        vbox.addSpacing(420)
        vbox.addLayout(hbox)
        vbox.addSpacing(420)
        vbox.addWidget(self.canvas)
        
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(vbox)
        self.setCentralWidget(self.centralWidget)



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
        array = get_array('Photos/Photo_Fiber_Obj_10X.tif')
        processed = get_processed_array(array)
        blank = get_contours_array(processed)
        peaks = get_peaks(blank, self.line)

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)

        # Maybe change to ax as input var for function?
        self.ax = self.figure.add_subplot(111)
        self.graph = self.ax.plot(peaks, blank[self.line,0:640][peaks], "x", c="red")
        self.graphx = self.ax.plot(range(0,640), blank[self.line,0:640])
        self.ax.set_title('Profiling of grayscale along the line')
        self.ax.set_ylabel('grayscale intensity')
        self.ax.set_xlabel('pixel')
        self.ax.set_ylim([-5,260])
        self.canvas.resize(1000,1000) 

    def clickup(self):
        """ One pixel up """
        self.line += 1
        self.updateplot()

    def clickdown(self):
        """ One pixel down """
        self.line -= 1
        self.updateplot()

    def textchanged(self, text):
        """ Intersection to the input pixel """
        if text == "" or not isinstance(int(text),int):
            print('not an integer')
        else: 
            self.line = int(text)

    def updateplot(self):
        value = self.line
        blank = self.blank
        peaks = self.peaks
        try: 
            value = float(value)
        except ValueError:
            value = 250

        # Renew graph
        if self.graph:
            line = self.graph.pop(0)
            line.remove()
            line = self.graphx.pop(0)
            line.remove()
        
        self.graph = self.ax.plot(peaks, blank[self.line,0:640][peaks], "x", c="red")
        self.graphx = self.ax.plot(range(0,640), blank[self.line,0:640])
        self.canvas.draw()

      

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyWindow()
    win.showMaximized()
    

    win.show()
    while True:
        sys.exit(app.exec_())