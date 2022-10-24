############################################################
#
# Socket client which sends a test frame to the display
# server.
#
# Writes 240 lines of 320 bytes for grayscale frame that is
# 320 columns x 240 rows.
#
############################################################

import sys
from socket import *

serverHost = 'localhost'
serverPort = 50007

frame = ['test data']

raw_input('hit any key')

if len(sys.argv) > 1:
	serverHost = sys.argv[1]
	if len(sys.argv) > 2:
		message = sys.argv[2:]

sockobj = socket(AF_INET, SOCK_STREAM)
sockobj.connect((serverHost, serverPort))

print 'connected to server'
raw_input('hit any key to send data')

for pixel in frame:
	print 'sending: ', `pixel`
	sockobj.send(pixel)
	data = sockobj.recv(1024)
	print 'Server responded:', `data`

print 'done with frame'
raw_input('hit any key to end session')

sockobj.close()
