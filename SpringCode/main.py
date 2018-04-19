from ControlSender import *
from CameraStream import *

import pygame
import cv2

import paramiko

def startRemoteControlReceiver():
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	piIP = '10.0.0.1'
	ssh.connect(piIP, port=22, username="pi", password="clss*")
	command = 'sudo -E python Documents/Spring\ Pi\ Code/test.py'
	stdin, stdout, stderr = ssh.exec_command(command)
	print('REMOTE RECEIVER STARTED'+str(stdout.read()))
	ssh.close()
	
startRemoteControlReceiver()

displayResolution = (640,480)
pygame.init()
screen=pygame.display.set_mode(displayResolution)

running = True

steering = 0
velocity = 0

steerStepUp = 0.2
steerStepDown = 0.2
velocityStepUp = 0.1
velocityStepDown = 0.3

controlSender = ControlSender()

cameraStream = CameraStream()
cameraStream.startStream()

while running:
	pygame.time.delay(100)
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			cameraStream.stopStream()
			running = False
	
	if not cameraStream.imageBufferIsEmpty:
		image = cameraStream.getFrame()
		image = cv2.resize(image, displayResolution)
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		image = pygame.image.frombuffer(image.tostring(), image.shape[1::-1], "RGB")
		imagerect = image.get_rect()
		screen.blit(image, imagerect)
		pygame.display.flip()
		
	keys = pygame.key.get_pressed()
	
	if keys[pygame.K_a]:
		if(steering>-1):
			steering -= steerStepUp
	else:
		if(steering<0):
			if(abs(steering)<steerStepDown):
				steering = 0
			else:
				steering += steerStepDown
			
	if keys[pygame.K_d]:
		if(steering<1):
			steering += steerStepUp
	else:
		if(steering>0):
			if(abs(steering)<steerStepDown):
				steering = 0
			else:
				steering -= steerStepDown	
			
	if keys[pygame.K_w]:
		if(velocity<1):
			velocity += velocityStepUp
	else:
		if(velocity>0):
			if(abs(velocity)<velocityStepUp):
				velocity = 0
			else:
				velocity -= velocityStepDown
			
	if keys[pygame.K_s]:
		if(velocity>-1):
			velocity -= velocityStepUp
	else:
		if(velocity<0):
			if(abs(velocity)<velocityStepDown):
				velocity = 0
			else:
				velocity += velocityStepDown

	print('')
	print('')
	print('steering: '+str(steering))
	print('velocity: '+str(velocity))
	
	try:
		controlSender.send('s'+str(steering))
		controlSender.send('v'+str(velocity/2))
	except Exception as e:
		print(str(e))
		controlSender.connect()