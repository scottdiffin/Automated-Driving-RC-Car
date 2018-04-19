import socket

class ControlSender():
	def __init__(self):
		self.host = '10.0.0.1' # IP of the Raspberry Pi
		self.port = 7626
		
	def connect(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.host, self.port))
		
	def send(self, message):
		self.sock.send(message.encode());