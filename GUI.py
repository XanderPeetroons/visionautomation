
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
        self.setWindowTitle("Tech")
        self.initUI()

    def initUI(self):
        # TEXT IMAGE
        self.textimage = QLabel(self)
        self.textimage.setText("Images")
        self.textimage.move(50,50)
        """
        # MOSFET IMAGE
        pixmapimage = QPixmap('Photos/mosfet.jpg')
        self.labelimage = QLabel(self)
        # pixmapimage = pixmapimage.scaled(scale,scale,Qt.KeepAspectRatio)
        self.labelimage.setPixmap(pixmapimage)

        # setting geometry to the label
        self.labelimage.setGeometry(0, -500, 2000, 2000)
        self.labelimage.show()


        # PROCESSED IMAGE
        # img = get_array('Photos/mosfet.jpg')
        # processed_array = get_processed_array(img)
        # cv2.imwrite('Photos/Test_gray.jpg', processed_array)

        pixmapprocessed = QPixmap('Photos/Test_gray.jpg')
        self.labelprocessed = QLabel(self)
        # pixmapimage = pixmapimage.scaled(scale,scale,Qt.KeepAspectRatio)
        self.labelprocessed.setPixmap(pixmapprocessed)

        # setting geometry to the label
        self.labelprocessed.setGeometry(800, -500, 2000, 2000)
        self.labelprocessed.show()
        """
        self.plot()

    def plot(self):
        array = get_array('Photos/mosfet.jpg')
        processed = get_processed_array(array)
        blank = get_contours_array(processed)
        peaks = get_peaks(blank, 250)

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)

        # Maybe change to ax as input var for function?
        ax = self.figure.add_subplot(111)
        ax.plot(peaks, blank[250,0:640][peaks], "x", c="red")
        ax.plot(range(0,640), blank[250,0:640])
        ax.set_title('Profiling of grayscale along the line')
        ax.set_ylabel('grayscale intensity')
        ax.set_xlabel('pixel')
        ax.set_ylim([-5,260])
        self.canvas.resize(1000,1000)
        # self.canvas.draw()
        # self.canvas.setGeometry(0,0,2000,2000)
        # self.show()
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.canvas)

        self.centralWidget = QWidget()
        self.centralWidget.setLayout(vbox)
        self.setCentralWidget(self.centralWidget)

      

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyWindow()
    win.showMaximized()
    


    win.show()
    while True:
        sys.exit(app.exec_())