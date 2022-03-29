# GUI
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import cv2
from Example_mv01 import *
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

# Resolution of the screen used
resolutionx = 3240
resolutiony = 2160


class GUI(QMainWindow):

    def __init__(self):
        super().__init__()

        # Window Initialization
        self.setWindowTitle('images')
    
        # setting geometry
        self.setGeometry(0, 0, 0, 0)
    
        # Set scene as central widget
        self.scene = Scene()
        self.setCentralWidget(self.scene)

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None,width=5,height=4,dpi=100):
        fig = Figure(figsize=(width,height),dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)



class Scene(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scener = QGraphicsScene()
        #self.images()
        self.plot()


    def images(self):

        # Defining the positions of the images
        imagex = 0
        imagey = -500
        processedx = 800
        processedy = -500

        # MOSFET IMAGE
        pixmapimage = QPixmap('Photos/mosfet.jpg')
        self.labelimage = QLabel(self)
        # pixmapimage = pixmapimage.scaled(scale,scale,Qt.KeepAspectRatio)
        self.labelimage.setPixmap(pixmapimage)

        # setting geometry to the label
        self.labelimage.setGeometry(imagex, imagey, 2000, 2000)
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
        self.labelprocessed.setGeometry(processedx, processedy, 2000, 2000)
        self.labelprocessed.show()

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
        self.canvas.draw()
        self.scener.addWidget(self.canvas)
        self.scener.show()

    





if __name__ == "__main__":
    app = QApplication([])
    win = GUI()
    win.showMaximized()
    
    # time.sleep(2)
    # for i in range(6):
    #     z = i%6
    #     win.updateSlider(z,5)
    # time.sleep(2)

    # app.processEvents()
    # time.sleep(6)
    # win.close()

    # app.quit()
    while True:
        sys.exit(app.exec_())