import cv2
import numpy as np
import requests
# from PyQt4.QtCore import *
# from PyQt4.QtGui import *
from PyQt5 import QtCore

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
#from PyQt4 import QtTest

import pyqtgraph as pg
import sys
import time
from process import Process
from webcam import Webcam
from video import Video
from interface import waitKey, plotXY

import matplotlib
matplotlib.use('Qt5Agg')

class Communicate(QObject):
    closeApp = pyqtSignal()
    
    
class GUI(QMainWindow, QThread):
    def __init__(self):
        super(GUI,self).__init__()
        self.initUI()
        self.setStyleSheet("background-color: white;")
        self.webcam = Webcam()
        self.video = Video()
        self.input = self.webcam
        # self.dirname = "http://10.39.1.138:8080/shot.jpg"
        print("Input: webcam")
        self.statusBar.showMessage("Input: webcam",4747)
        self.btnOpen.setEnabled(False)
        self.process = Process()
        self.status = False
        self.frame = np.zeros((10,10,3),np.uint8)
        #self.plot = np.zeros((10,10,3),np.uint8)
        #self.url = "http://10.39.1.138:8080/shot.jpg"
        self.bpm = 0



    def initUI(self):

        #set font
        font = QFont()
        font.setPointSize(16)

        #set font2
        font2 = QFont()
        font2.setPointSize(24)
        
        #widgets
        self.btnStart = QPushButton("Start", self)
        self.btnStart.move(440,960)
        self.btnStart.setFixedWidth(200)
        self.btnStart.setFixedHeight(50)
        self.btnStart.setFont(font)
        self.btnStart.clicked.connect(self.run)
        self.btnStart.setStyleSheet("QPushButton { background-color: rgb(255, 255,255) }"
                        "QPushButton:pressed { background-color: rgb(0, 67, 255) ; color: white }" )
        
        self.btnOpen = QPushButton("Open", self)
        self.btnOpen.move(230,960)
        self.btnOpen.setFixedWidth(200)
        self.btnOpen.setFixedHeight(50)
        self.btnOpen.setFont(font)
        self.btnOpen.clicked.connect(self.openFileDialog)
        self.btnOpen.setStyleSheet("QPushButton { background-color: rgb(255, 255,255) }"
                        "QPushButton:pressed { background-color: rgb(0, 67, 255); color: white }" )
        
        self.cbbInput = QComboBox(self)
        self.cbbInput.addItem("Webcam")
        self.cbbInput.addItem("Video")
        # self.cbbInput.addItem("IPCamera")
        self.cbbInput.setCurrentIndex(0)
        self.cbbInput.setFixedWidth(200)
        self.cbbInput.setFixedHeight(50)
        self.cbbInput.move(20,960)
        self.cbbInput.setFont(font)
        self.cbbInput.activated.connect(self.selectInput)

        #Adding Logos--------------------------------
        self.labelImage  = QLabel(self)
        self.pixmap = QPixmap("Analytica_Logo1.png")
        #pixmap = pixmap.scaled(535, 2070, QtCore.Qt.KeepAspectRatio)
        self.labelImage .setPixmap(self.pixmap)
        self.labelImage.resize(self.pixmap.width(),
                               self.pixmap.height())
        self.labelImage .move(1400, 940)

        self.labelImage2  = QLabel(self)
        self.pixmap = QPixmap("VisionHR_Logo.png")
        self.labelImage2 .setPixmap(self.pixmap)
        self.labelImage2.resize(self.pixmap.width(),
                           self.pixmap.height())
        self.labelImage2 .move(1400, 540)
        #self.show()
        #--------------------------------------------

        self.lblDisplay = QLabel(self) #label to show frame from camera
        self.lblDisplay.setGeometry(50,20,640,480)
        self.lblDisplay.setStyleSheet("background-color: #FFFFFF")
        
        self.lblROI = QLabel(self) #label to show face with ROIs
        self.lblROI.setGeometry(700,20,640,480)
        self.lblROI.setStyleSheet("background-color: #FFFFFF")
        
        self.lblHR = QLabel(self) #label to show HR change over time
        self.lblHR.setGeometry(1450,70,300,40)
        self.lblHR.setFont(font2)
        self.lblHR.setText("Frequency: ")
        
        self.lblHR2 = QLabel(self) #label to show stable HR
        self.lblHR2.setGeometry(1450,120,500,90)
        self.lblHR2.setFont(font2)
        self.lblHR2.setText("Heart rate: ")
        
        # self.lbl_Age = QLabel(self) #label to show stable HR
        # self.lbl_Age.setGeometry(1450,170,300,40)
        # self.lbl_Age.setFont(font2)
        # self.lbl_Age.setText("Age: ")
        #
        # self.lbl_Gender = QLabel(self) #label to show stable HR
        # self.lbl_Gender.setGeometry(1450,220,300,40)
        # self.lbl_Gender.setFont(font2)
        # self.lbl_Gender.setText("Gender: ")
        pg.setConfigOption('background', 'w')
        #dynamic plot
        self.signal_Plt = pg.PlotWidget(self)
        self.signal_Plt.move(20,540)
        self.signal_Plt.resize(1080,192)
        self.signal_Plt.setLabel('bottom', "Signal")

        
        self.fft_Plt = pg.PlotWidget(self)
        #self.fft_Plt.setConfigOption('background', 'w')
        self.fft_Plt.move(20,750)
        self.fft_Plt.resize(1080,192)
        self.fft_Plt.setLabel('bottom', "FFT") 
        
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(200)
        
        
        self.statusBar = QStatusBar()
        self.statusBar.setFont(font)
        self.setStatusBar(self.statusBar)
        
        #event close
        self.c = Communicate()
        self.c.closeApp.connect(self.close)
        
        #event change combobox index
        
        #config main window
        self.setGeometry(100,100,1160,640)
        #self.center()
        self.setWindowTitle("Heart rate monitor")
        #self.show()
        self.showFullScreen()
        #self.showMaximized()

        
        
    def update(self):
        #z = np.random.normal(size=1)
        #u = np.random.normal(size=1)
        self.signal_Plt.clear()
        self.signal_Plt.plot(self.process.samples[20:],pen='r')

        self.fft_Plt.clear()
        self.fft_Plt.plot(np.column_stack((self.process.freqs, self.process.fft)), pen = '#000000')
        
        
   
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def closeEvent(self, event):
        reply = QMessageBox.question(self,"Message", "Are you sure want to quit",
            QMessageBox.Yes|QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            event.accept()
            self.input.stop()
            cv2.destroyAllWindows()
        else: 
            event.ignore()
    
    def selectInput(self):
        self.reset()
        if self.cbbInput.currentIndex() == 0:
            self.input = self.webcam
            print("Input: webcam")
            self.btnOpen.setEnabled(False)
            #self.statusBar.showMessage("Input: webcam",5000)
        elif self.cbbInput.currentIndex() == 1:
            self.input = self.video
            print("Input: video")
            self.btnOpen.setEnabled(True)
            #self.statusBar.showMessage("Input: video",5000)
        # elif self.cbbInput.currentIndex() == 2:
        #     self.input = self.url
        #     print("Input: IPCamera")
        #     self.btnOpen.setEnabled(False)
        
    
    def mousePressEvent(self, event):
        self.c.closeApp.emit()    
    
    # def make_bpm_plot(self):
    
        # plotXY([[self.process.times[20:],
                     # self.process.samples[20:]],
                    # [self.process.freqs,
                     # self.process.fft]],
                    # labels=[False, True],
                    # showmax=[False, "bpm"],
                    # label_ndigits=[0, 0],
                    # showmax_digits=[0, 1],
                    # skip=[3, 3],
                    # name="Plot",
                    # bg=None)
        
        # fplot = QImage(self.plot, 640, 280, QImage.Format_RGB888)
        # self.lblPlot.setGeometry(10,520,640,280)
        # self.lblPlot.setPixmap(QPixmap.fromImage(fplot))
    
    def key_handler(self):
        """
        cv2 window must be focused for keypresses to be detected.
        """
        self.pressed = waitKey(1) & 255  # wait for keypress for 10 ms
        if self.pressed == 27:  # exit program on 'esc'
            print("[INFO] Exiting")
            self.webcam.stop()
            sys.exit()
    
    def openFileDialog(self):
        self.dirname = QFileDialog.getOpenFileName(self, 'OpenFile',r"C:\Users\uidh2238\Desktop\test videos")
        #self.statusBar.showMessage("File name: " + self.dirname,5000)
    
    def reset(self):
        self.process.reset()
        self.lblDisplay.clear()
        self.lblDisplay.setStyleSheet("background-color: #FFFFFF")

    @QtCore.pyqtSlot()
    def main_loop(self):
        frame = self.input.get_frame()

        self.process.frame_in = frame
        self.process.run()
        
        #cv2.imshow("Processed", frame)
        
        self.frame = self.process.frame_out #get the frame to show in GUI
        self.f_fr = self.process.frame_ROI #get the face to show in GUI
        #print(self.f_fr.shape)
        self.bpm = self.process.bpm #get the bpm change over the time
        
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
        cv2.putText(self.frame, "FPS "+str(float("{:.2f}".format(self.process.fps))),
                       (20,460), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 255),2)
        img = QImage(self.frame, self.frame.shape[1], self.frame.shape[0], 
                        self.frame.strides[0], QImage.Format_RGB888)
        self.lblDisplay.setPixmap(QPixmap.fromImage(img))
        
        self.f_fr = cv2.cvtColor(self.f_fr, cv2.COLOR_RGB2BGR)
        #self.lblROI.setGeometry(660,10,self.f_fr.shape[1],self.f_fr.shape[0])
        self.f_fr = np.transpose(self.f_fr,(0,1,2)).copy()
        f_img = QImage(self.f_fr, self.f_fr.shape[1], self.f_fr.shape[0], 
                       self.f_fr.strides[0], QImage.Format_RGB888)
        self.lblROI.setPixmap(QPixmap.fromImage(f_img))
        
        self.lblHR.setText("Freq: " + str(float("{:.2f}".format(self.bpm))) + " Hz")
        
        if self.process.bpms.__len__() >50:
            if(max(self.process.bpms-np.mean(self.process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
                self.lblHR2.setText("Heart rate: " + str(float("{:.2f}".format(np.mean(self.process.bpms)))) + " bpm")

        #self.lbl_Age.setText("Age: "+str(self.process.age))
        #self.lbl_Gender.setText("Gender: "+str(self.process.gender))
        #self.make_bpm_plot()#need to open a cv2.imshow() window to handle a pause 
        #QtTest.QTest.qWait(10)#wait for the GUI to respond
        self.key_handler()  #if not the GUI cant show anything

    def run(self, input):
        self.reset()
        input = self.input
        self.input.dirname = self.dirname
        if self.input.dirname == "" and self.input == self.video:
            print("choose a video first")
            #self.statusBar.showMessage("choose a video first",5000)
            return
        # if self.input.dirname == "http://10.39.1.138:8080/shot.jpg" and self.input == self.url:
        #     while True:
        #         img_resp = requests.get(url)
        #         img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
        #         img = cv2.imdecode("IPCamera", img)
        #         cv2.imshow("IPCamera", img)
        #         if cv2.waitKey(1)==27:
        #             break

        if self.status == False:
            self.status = True
            input.start()
            self.btnStart.setText("Stop")
            self.cbbInput.setEnabled(False)
            self.btnOpen.setEnabled(False)
            self.lblHR2.clear()
            while self.status == True:
                self.main_loop()
        elif self.status == True:
            self.status = False
            input.stop()
            self.btnStart.setText("Start")
            self.cbbInput.setEnabled(True)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GUI()
    while ex.status == True:
        ex.main_loop()

    sys.exit(app.exec_())
