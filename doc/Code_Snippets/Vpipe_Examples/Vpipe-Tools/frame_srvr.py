############################################################
#
# Socket server which receives frames from client for
# display.
#
# Reads 240 lines of 320 bytes for grayscale frame that is
# 320 columns x 240 rows.
#
############################################################

from socket import *

myHost = ''
myPort = 50007

sockobj = socket(AF_INET, SOCK_STREAM)
sockobj.bind((myHost, myPort))
sockobj.listen(5)

while 1:
	connection, address = sockobj.accept()
	print 'Sever connected to by', address
	while 1:
		data = connection.recv(307200)		# one frame
		if not data: break
		print 'data = ', `data`
		connection.send('Frame received')
	connection.close()
	print 'connection closed'

raw_input('hit any key')
