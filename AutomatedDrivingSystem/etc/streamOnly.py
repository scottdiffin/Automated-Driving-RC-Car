import CameraStream
import paramiko
import socket

import cv2


displayResolution = (640,480)
cv2.namedWindow('display')

camera = CameraStream.CameraStream()

camera.startStream()

while camera.isStreaming:
    if not camera.imageBufferIsEmpty:
        work = camera.getFrame()
        work = cv2.flip(work,0)
        
        resizedImage = cv2.resize(work,displayResolution)
        cv2.imshow('display', resizedImage)
        cv2.waitKey(1)

camera.stopStream()

cv2.destroyAllWindows()
