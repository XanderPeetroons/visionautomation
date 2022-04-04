
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
        ### Variable for horizontal pixel
        self.line = 1000

        ### FONT VARIABLE
        self.fontvar = QFont('Times', 16)
        self.fontvar.setBold(True)

        ### TEXTS
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
        
        ### CHIP_FIBER IMAGE
        pixmapimage = QPixmap('Photos/Photo_Fiber_Obj_10X.tif')
        pixmapimage = pixmapimage.scaled(700, 700, Qt.KeepAspectRatio)
        self.labelimage = QLabel(self)
        self.labelimage.setPixmap(pixmapimage)
        self.labelimage.setGeometry(20,200,700,700)



        ### PROCESSED IMAGE

        img = get_array('Photos/Photo_Fiber_Obj_10X.tif')
	## Processed array now will include contour (to compatible with adaptive threshold, which not require contour)
        processed_array = get_processed_array(img) 
        cv2.imwrite('Photos/Processed_10X.jpg', processed_array)

        pixmapprocessed = QPixmap('Photos/Processed_10X.jpg')
        self.labelprocessed = QLabel(self)
        pixmapprocessed = pixmapprocessed.scaled(700,700,Qt.KeepAspectRatio)
        self.labelprocessed.setPixmap(pixmapprocessed)
        self.labelprocessed.setGeometry(800,200,700,700)

        ### BUTTONS
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


        ### PLOT
        self.plot()

        vboxbuttons = QVBoxLayout()
        vboxbuttons.addWidget(self.bup)
        vboxbuttons.addWidget(self.textline)
        vboxbuttons.addWidget(self.bdown)

        hbox = QHBoxLayout()
        hbox.addSpacing(1500)
        hbox.addLayout(vboxbuttons)

        # hboxtop = QHBoxLayout()
        # hboxtop.addWidget(self.labelimage)
        # hboxtop.addWidget(self.labelprocessed)
        # hboxtop.addStretch(1)

        # hboxbottom = QHBoxLayout()
        # hboxbottom.addWidget(self.canvas)
        # hboxbottom.addStretch(1)

        vbox = QVBoxLayout()
        # vbox.addSpacing(1000)
        vbox.addSpacing(420)
        vbox.addLayout(hbox)
        vbox.addSpacing(420)
        vbox.addWidget(self.canvas)
        
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(vbox)
        self.setCentralWidget(self.centralWidget)

    def plot(self):
        array = get_array('Photos/Photo_Fiber_Obj_10X.tif')
        processed = get_processed_array(array)
        # blank = get_contours_array(processed)
        peaks = get_peaks(processed, self.line)

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)

        ### Maybe change to ax as input var for function?
        ax = self.figure.add_subplot(111)
        ax.plot(peaks, processed[self.line,:][peaks], "x", c="red")
        ax.plot(range(0, processed.shape[1]), processed[self.line,:])
        ax.set_title('Profiling of grayscale along the line')
        ax.set_ylabel('Grayscale intensity')
        ax.set_xlabel('Pixel')
        ax.set_ylim([-5,260]) ### Grayscale from 0 to 255
        self.canvas.resize(1000,1000)
        # self.canvas.draw()
        # self.canvas.setGeometry(0,0,2000,2000)
        # self.show()     

    def clickup(self):
        self.line += 1
        self.plot()
        self.canvas.draw()
        print("no")

    def clickdown(self):
        self.line -= 1
        # self.plot()
        print("yes")

    def textchanged(self, text):
        if not isinstance(int(text),int):
            print('not an integer')
        else: 
            self.line = int(text)



      

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyWindow()
    win.showMaximized()
    


    win.show()
    while True:
        sys.exit(app.exec_())