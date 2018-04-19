import io
import socket
import struct

import platform
import subprocess

from threading import Thread

from PIL import Image
import numpy as np
import cv2

import paramiko

class CameraStream:
    
    def __init__(self, resolution=(1280,720), framerate=30):
        self.streamResolution = resolution
        self.framerate = framerate
        self.imageBuffer = cv2.imdecode(np.zeros(self.streamResolution), 1)
        self.imageBufferIsEmpty = True
        
    def startStream(self):
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.socket.bind(('', 5267))
        self.socket.listen(0)
        self.isStreaming = True
        Thread(target=self.streamLoop).start()
        Thread(target=self.beginRemoteStream).start()
        
    def stopStream(self):
        self.isStreaming = False
        self.socket.close()
        
    def getFrame(self):
        return self.imageBuffer
        
    def streamLoop(self):
        connection = self.socket.accept()[0].makefile('rb')
        try:
            while self.isStreaming:
                # Read the length of the image as a 32-bit unsigned int. If the
                # length is zero, quit the loop
                image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
                if not image_len:
                    connection.close()
                    self.socket.close()
                    self.isStreaming = False
                    break
                # Construct a stream to hold the image data and read the image
                # data from the connection
                stream_message = connection.read(image_len)
                image_stream = io.BytesIO()
                image_stream.write(stream_message)
                # Rewind the stream, open it as an image with PIL and do some
                # processing on it
                image_stream.seek(0)
                image = Image.open(image_stream)
                np_arr = np.fromstring(stream_message, np.uint8)
                self.imageBuffer = cv2.imdecode(np_arr, 1)
                self.imageBufferIsEmpty = False
        finally:
            connection.close()
            self.imageBuffer = cv2.imdecode(np.zeros(self.streamResolution), 1)
            self.imageBufferIsEmpty = True
            
    def beginRemoteStream(self):
        piIP = '10.0.0.1'
        # SSH into the pi to start the streaming script
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(piIP, port=22, username="pi", password="clss*")
        # use mysocket to find the ip of the controller, then send it to the pi
        mysocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        mysocket.connect(("8.8.8.8", 80))
        resolutionString = str(self.streamResolution[0]) + "x" + str(self.streamResolution[1])
        command = "python Documents/AutomatedDrivingSystem/streamCamera.py " + mysocket.getsockname()[0] + " " + resolutionString + " " + str(self.framerate)
        mysocket.close()
        print command
        stdin, stdout, stderr = ssh.exec_command(command)
        print stdout.read()
        ssh.close()