############################################################
#
# Displays PPM frame from file.
#
# Reads 240 lines of 320 bytes for grayscale frame that is
# 320 columns x 240 rows.
#
############################################################

from Tkinter import *
from quit import Quit
from glob import glob
from tkFileDialog import askopenfilename

def openFile():
	filename = askopenfilename()
	print 'filename = ', filename
	img = PhotoImage(file=filename)
	mcanvas.config(height=img.height(), width=img.width())
	mcanvas.create_image(2, 2, image=img, anchor=NW)

root = Tk()

statfont = ('times', 10, 'bold')
statwin = Label(root, text='V-pipe Display Tool')
statwin.config(bg='white', fg='black')
statwin.config(font=statfont)
statwin.pack(side=TOP, expand=YES, fill=BOTH)

Quit(root).pack(side=TOP)

btn = Button(root, text='Open File ...', command=openFile)    
btn.pack(side=TOP)

mcanvas = Canvas(root, bg='white')
mcanvas.pack(side=LEFT, expand=YES, fill=BOTH)
img = PhotoImage(file="test_frame.ppm")
mcanvas.config(height=img.height(), width=img.width())
mcanvas.create_image(2, 2, image=img, anchor=NW)


root.mainloop()
