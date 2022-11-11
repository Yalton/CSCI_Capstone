############################################################
#
# Generates a test PGM format frame in a file to test load.
#
# Writes 240 lines of 320 bytes for color frame that is
# 320 columns x 240 rows with 3 bytes per pixel
#
############################################################

import sys
import struct
from socket import *
serverHost = 'localhost'
serverPort = 50007

sockobj = socket(AF_INET, SOCK_STREAM)
sockobj.connect((serverHost, serverPort))

raw_input('hit any key to generate test frames')

myfile = open('test_frame.ppm', 'rb')
frame1 = myfile.read(230421)

frame2 = frame1[0:21] + frame1[57621:115221] + frame1[115221:172821] + frame1[172821:230421] + frame1[21:57621]
frame3 = frame1[0:21] + frame1[115221:172821] + frame1[172821:230421] + frame1[21:57621] + frame1[57621:115221]
frame4 = frame1[0:21] + frame1[172821:230421] + frame1[21:57621] + frame1[57621:115221] + frame1[115221:172821]

stream = [frame1, frame2, frame3, frame4]

print 'Closing file'
myfile.close()

while 1:
	for i in range(4):
		#print 'Sending frame = ', i, ' with length = ', len(stream[i])
		sockobj.send(stream[i])
		#raw_input('Frame sent, hit any key to continue with next')

print 'Closing connection'
sockobj.close()
