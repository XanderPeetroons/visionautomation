# GUI
from tkinter.tix import IMAGETEXT
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import cv2
# from Example_mv01 import *
import sys

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


class Slider(QGraphicsRectItem):
    def __init__(self,x,y,w,h):
        super().__init__(x,y,w,h)
        self.setPen(Qt.darkGreen)
        self.setBrush(Qt.darkGreen)

    def updateSliderPosition(self, state, nbstates=5):
        lengthBar = (600/3240 * resolutionx) - (20/3240 * resolutionx)
        deltax = lengthBar/nbstates
        self.setPos(0 + state*deltax,0)


class Scene(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.images()
        self.sceneview = QGraphicsScene()
        self.setSceneRect(0,0,5,5)
        self.slider = Slider(0,0,20/3240 * resolutionx,70/2160 * resolutiony)
        self.sceneview.addItem(self.slider)


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