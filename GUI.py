# GUI
from tkinter.tix import IMAGETEXT
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import cv2

# Resolution of the screen used
resolutionx = 3240
resolutiony = 2160

class Scene(QGraphicsView):
    def __init__(self):
            super().__init__()
            self.images()


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
        pixmapprocessed = QPixmap('Photos/mosfet.jpg')
        self.labelprocessed = QLabel(self)
        # pixmapimage = pixmapimage.scaled(scale,scale,Qt.KeepAspectRatio)
        self.labelprocessed.setPixmap(pixmapprocessed)

        # setting geometry to the label
        self.labelprocessed.setGeometry(processedx, processedy, 2000, 2000)
        self.labelprocessed.show()

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


# class MovingObject(QGraphicsRectItem):
#     def __init__(self,x,y,w,h):
#         super().__init__(x,y,w,h)
#         self.setPen(Qt.darkGreen)
#         self.setBrush(Qt.darkGreen)

#     def updateSliderPosition(self, state, nbstates=5):
#         lengthBar = (600/3240 * resolutionx) - (20/3240 * resolutionx)
#         deltax = lengthBar/nbstates
#         self.setPos(0 + state*deltax,0)

# class Bar(QGraphicsRectItem):
#     def __init__(self,x,y,w,h):
#         super().__init__(x,y,w,h)
#         self.setPen(Qt.white)
#         self.setBrush(Qt.darkGray)



# class Scene(QGraphicsView):

#     def __init__(self):
#         super().__init__()

#         self.scener = QGraphicsScene()
#         self.setScene(self.scener)
#         self.setSceneRect(0,0,5,5)

#         # Add Bar
#         self.bar = Bar(-340/3240 *resolutionx,-30/2160 *resolutiony,600/3240 *resolutionx,9/2160 * resolutiony)
#         self.scener.addItem(self.bar)

#         # Add the slider
#         self.movingObject = MovingObject(-340/3240 * resolutionx,-60/2160 * resolutiony,20/3240 * resolutionx,70/2160 * resolutiony)
#         self.scener.addItem(self.movingObject)

#         # Place the speech icons
#         self.iconLabels()
#         self.showLabels(None)
    
    
#     def iconLabels(self):
#         """
#         Add the speech and text labels
#         """

#         icon1x = 3230#950/3240 * resolutionx
#         icon1y = 800/2160 * resolutiony
#         icon2x = 2000/3240 * resolutionx
#         icon2y = 800/2160 * resolutiony
#         scale = 200/3240 * resolutionx

#         # label width
#         self.l_width = 200/3240 * resolutionx
#         # label height
#         self.l_height = 200/2160 * resolutiony
        
#         # Create labels for speech icons
#         # Left Speaker icon 1
#         pixmapgreenleft = QPixmap('greenspeechicon.png')
#         self.labelgreenleft = QLabel(self)
#         pixmapgreenleft = pixmapgreenleft.scaled(scale,scale,Qt.KeepAspectRatio)
#         self.labelgreenleft.setPixmap(pixmapgreenleft)
#         # setting geometry to the label
#         self.labelgreenleft.setGeometry(icon1x, icon1y, self.l_width, self.l_height)

#         pixmap1 = QPixmap('SpeechIcon1.png')
#         self.label1 = QLabel(self)
#         pixmap1 = pixmap1.scaled(scale,scale,Qt.KeepAspectRatio)
#         self.label1.setPixmap(pixmap1) 
#         # setting geometry to the label
#         self.label1.setGeometry(icon1x, icon1y, self.l_width, self.l_height)



#         # Right Speaker icon 2
#         pixmapgreenright = QPixmap('greenspeechicon.png')
#         self.labelgreenright = QLabel(self)
#         pixmapgreenright = pixmapgreenright.scaled(scale,scale,Qt.KeepAspectRatio)
#         # Mirror image for the right speaker
#         transform = QTransform()
#         transform.scale(-1,1)
#         pixmapgreenright = pixmapgreenright.transformed(transform)
#         self.labelgreenright.setPixmap(pixmapgreenright) 
#         # setting geometry to the label
#         self.labelgreenright.setGeometry(icon2x, icon2y, self.l_width, self.l_height)

#         pixmap2 = QPixmap('SpeechIcon1.png')
#         self.label2 = QLabel(self)
#         pixmap2 = pixmap2.scaled(scale,scale,Qt.KeepAspectRatio)
#         # Mirror image for the right speaker
#         transform = QTransform()
#         transform.scale(-1,1)
#         pixmap2 = pixmap2.transformed(transform)
#         self.label2.setPixmap(pixmap2) 
#         # setting geometry to the label
#         self.label2.setGeometry(icon2x, icon2y, self.l_width, self.l_height)

#         # Text instructions labels
#         self.labeltextleft = QLabel(self)
#         self.labeltextleft.setText("Please listen to the left speaker")
#         self.labeltextleft.setFont(QFont("Times",50))
#         self.labeltextleft.move(800/3240 *resolutionx, 800/2160 *resolutiony)
        
#         self.labeltextright = QLabel(self)
#         self.labeltextright.setText("Please listen to the right speaker")
#         self.labeltextright.setFont(QFont("Times",50))
#         self.labeltextright.move(800/3240 * resolutionx, 800/2160 *resolutiony)

#     def showLabels(self,function):
#         """
#         Show the labels according to the state of the system
#         """
#         if function == "left" or function is None:
#             self.labeltextleft.hide()
#             self.labeltextright.hide()
#             self.label1.hide()
#             self.label2.show()
#             self.labelgreenleft.show()
#             self.labelgreenright.hide()
#         elif function == "right":
#             self.labeltextleft.hide()
#             self.labeltextright.hide()
#             self.label2.hide()
#             self.label1.show()
#             self.labelgreenright.show()
#             self.labelgreenleft.hide()

#         elif function == "leftinstructions" or function == "rightinstructions":
#             self.labelgreenright.hide()
#             self.labelgreenleft.hide()
#             self.label1.hide()
#             self.label2.hide()
#             if function == "leftinstructions":
#                 self.labeltextleft.show()
#                 self.labeltextright.hide()
                
#             elif function == "rightinstructions":
#                 self.labeltextright.show()
#                 self.labeltextleft.hide()
                

#     # Method is called every time the audio gain changes
#     def updateSlider(self, state, nbstates):
#         """
#         Update the slider every time a decision is made
#         """
#         self.movingObject.updateSliderPosition(state, nbstates)
#         QApplication.processEvents()
#         time.sleep(1)






# class GUI(QMainWindow):

#     def __init__(self):
#         super().__init__()

#         # Window Initialization
#         self.setWindowTitle('Audio gain of the headphones')
    
#         # setting geometry
#         self.setGeometry(0, 0, 0, 0)
    
#         # Set scene as central widget
#         self.scene = Scene()
#         self.setCentralWidget(self.scene)

#     def updateSlider(self, state, nbstates):
#         self.scene.updateSlider(state, nbstates)
#         self.scene.bar.setPos(0,0)
    
#     def updateSliderFocus(self,state,nbstates,direction):
#         self.scene.showLabels(direction)
#         self.scene.updateSlider(state,nbstates)
#         self.scene.bar.setPos(0,0)

#     def trainingSide(self, direction):
#         self.scene.showLabels(direction)
#         self.scene.movingObject.setPos(10000000,1000000)
#         self.scene.bar.setPos(0,0)

#     def showInstructions(self,function):
#         self.scene.showLabels(function)
#         self.scene.movingObject.setPos(10000000,1000000)
#         self.scene.bar.setPos(10000000,10000000)








if __name__ == "__main__":
    app = QApplication([])
    win = GUI()
    win.showMaximized()
    
    # time.sleep(2)
    # for i in range(6):
    #     z = i%6
    #     win.updateSlider(z,5)
    # time.sleep(2)

    app.processEvents()
    time.sleep(6)
    win.close()

    app.quit()