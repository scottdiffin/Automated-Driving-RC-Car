import cv2
import vision

import numpy as np

from matplotlib import pyplot as plt

from CameraStream import CameraStream

import glob

'''
camera = CameraStream()
camera.startStream()
while camera.imageBufferIsEmpty:
    print 'waiting'
distorted = camera.getFrame()
camera.stopStream()
'''

images = glob.glob('test_track/track*')

cv2.namedWindow('image',cv2.WINDOW_NORMAL)
cv2.resizeWindow('image',600,400)

for fname in images:
    image = cv2.imread(fname)
    image = cv2.resize(image,(1280,720))
    image = vision.detectLanes(image)
    
    cv2.imshow('image',image)
    cv2.waitKey(4000)
    