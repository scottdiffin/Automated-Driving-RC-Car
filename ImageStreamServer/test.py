import io
import socket
import struct
from PIL import Image

import threading

import pygame

import numpy as np
import cv2

# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# all interfaces)
server_socket = socket.socket()
server_socket.bind(('', 5267))
server_socket.listen(0)

displaySize = (640,480)

cv2.namedWindow('frame');

def displayFrame(image):
    resizedImage = cv2.resize(image, displaySize)
    cv2.imshow('frame', resizedImage)
    cv2.waitKey(1)

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('rb')
try:
    while True:
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            connection.close()
            server_socket.close()
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
        print('Image is %dx%d' % image.size)
        #image.verify()
        print('Image is verified')
        
        np_arr = np.fromstring(stream_message, np.uint8)
        image = cv2.imdecode(np_arr, 1)
        average_color = [image[:, :, i].mean() for i in range(image.shape[-1])]
        output = average_color[0]+average_color[1]+average_color[2];
        output = 'bright' if (output>200) else 'dark'
        print output
        displayFrame(image)
finally:
    connection.close()
    server_socket.close()
    cv2.destroyAllWindows()
