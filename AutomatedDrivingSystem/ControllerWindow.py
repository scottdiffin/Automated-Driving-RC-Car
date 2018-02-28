import Tkinter as tk
import tkSimpleDialog

import cv2
from PIL import ImageTk, Image

from threading import Thread

import vision
from CameraStream import CameraStream


def cvToTkImage(image, size=None):
    b,g,r = cv2.split(image)
    cvImage = cv2.merge((r,g,b))
    pilImage = Image.fromarray(cvImage)
    if size!=None:
        pilImage = pilImage.resize(size)
    tkImage = ImageTk.PhotoImage(image=pilImage) 
    return tkImage

class ControllerWindow():
    
    def __init__(self, parent):
        self.parent = parent
        self.parent.title("Automated Driving System")
        self.parent.geometry("800x600")
        self.parent.protocol("WM_DELETE_WINDOW", self.onClosing)
        
        self.camera = CameraStream()
        
        self.videoFeedResolution = (480,360)
        self.videoFramerate = 30
        cvImage = cv2.imread("resources/blank.jpg",1)
        self.blankFrame = cvToTkImage(cvImage, self.videoFeedResolution)
        self.videoFeed = tk.Label(self.parent, image=self.blankFrame)
        self.videoFeed.place(x=0,y=0)
        
        self.startStreamButton = tk.Button(self.parent, text="Start Stream", command=self.startStream)
        self.startStreamButton.place(x=self.videoFeedResolution[0]+10,y=0)
        
        self.stopStreamButton = tk.Button(self.parent, text="Stop Stream", command=self.stopStream)
        self.stopStreamButton.place(x=self.videoFeedResolution[0]+10,y=25)
        
        self.screenshotButton = tk.Button(self.parent, text="Take Screenshot", command=self.screenshot)
        self.screenshotButton.place(x=self.videoFeedResolution[0]+10,y=50)
        
    def onClosing(self):
        if self.camera.isStreaming:
            self.stopStream()
        self.parent.destroy()
        
    def screenshot(self):
        if self.camera.isStreaming and not self.camera.imageBufferIsEmpty:
            screenshot = self.camera.getFrame()
            screenshot = cv2.flip(screenshot,0)
            filename = tkSimpleDialog.askstring("Screenshot", "Please enter a file name:")
            cv2.imwrite("resources/"+filename, screenshot)
        
    def startStream(self):
        self.camera.startStream()
        self.videoThreadID = self.parent.after(1000/self.videoFramerate, self.updateFrame)
        
    def stopStream(self):
        self.parent.after_cancel(self.videoThreadID)
        self.videoFeed.configure(image=self.blankFrame)
        self.camera.stopStream()
        
    def updateFrame(self):
        if not self.camera.imageBufferIsEmpty:
            work = self.camera.getFrame()
            work = cv2.flip(work,0)
            #work = vision.undistort(work)
            
            #work = vision.detectLanes(work)
            
            self.frame = cvToTkImage(work, self.videoFeedResolution)
            self.videoFeed.configure(image=self.frame)
        self.videoThreadID = self.parent.after(1000/self.videoFramerate, self.updateFrame)