#Creation Date 9/7/22
#Author: Dalton Bailey 
#Course: CSCI 490
#Instructor Sam Siewert

from tkinter import *
import tkinter as tk
from tkinter import ttk
import numpy as np
import cv2 as cv
import matplotlib as plot
import atexit
from os.path import exists
from themes import *

#Request class; Object for storing data about individual requests that the user has made
class request():
    #Constructor for Request object
    def __init__(self):
        self.name = "NULL"
        self.manufacturer= "NULL"
        self.SKU= "NULL"
        self.release= "NULL"
        self.desiredprice= "NULL"
        self.maxprice= "NULL"
        self.notify= "NULL"

#Interface class; data structure to hold information about the user of the program and functions to make the GUI. 
class interface():
 
    #Constructor for Interface object
    def __init__(self):
        self.root = Tk() # Calls tktinker object and sets self.root to be equal to it
        userdataarray = []

        file_exists = exists('userdata.txt') #Check if userdaata file exists in current directory 

        if file_exists == 0: #If file DNE create a fresh one and set all values to NULL
            UserDatafile = open("userdata.txt", "w") 
            UserData = ["NULL\n","NULL\n","NULL\n","NULL\n","NULL\n","NULL\n"]
            UserDatafile.writelines(UserData)
            UserDatafile.close()

        #Open userdata file, and save values to an array
        with open('userdata.txt') as file:
            for line in file:
                userdataarray.append(line)
        file.close() 

        #Set userata in interface object to be equal to values pulled from the userdata file
        self.name = userdataarray[0]
        self.email = userdataarray[1]
        self.saddr = userdataarray[2]
        self.baddr = userdataarray[3]
        self.ccfile = userdataarray[4]
        self.spendlimit = userdataarray[5]
        print (self.name)
        if self.name == "NULL\n" or self.email == "NULL" or self.saddr == "NULL" or self.baddr == "NULL" or self.ccfile == "NULL" or self.spendlimit == "NULL": 
            self.giveninfo = "False"
        else: 
            self.giveninfo = "True"
        
        print(self.giveninfo)
        self.notify= "NULL"
        self.requesteditems = []
    
    #Function to create the "View Requests" Window
    def view_request(self): 
        if self.giveninfo == "False":
            self.error_window() #Open up error gui window
        else: 
            window = tk.Toplevel(self.root) #Create new window and base it off orginal window
            window.configure(background="#666666") #Set background color
            window.geometry("676x856") #Set size of window
            label = Label(window, text='Viewing previous requests', font=("Arial", 15), fg='white', bg='#666666', height=2, width=20)
            label.place(relx=0.5, rely=0, anchor=N)
            separator1 = ttk.Separator(window, orient='horizontal') # Create Horizontal seperator bar
            separator1.place(relx=0, rely=0.04, relwidth=1, relheight=0.005)
            separator2 = ttk.Separator(window, orient='vertical') # Create vertical seperator bar
            separator2.place(relx=0.05, rely=0.04, relwidth=0.005, relheight=1)



    #Function to create the "Create Request" Window  
    def create_request(self): 
        if self.giveninfo == "False":
            self.error_window() #Open up error gui window
        else: 
            requestitem = request()
            def get_name_input():
                requestitem.name=inputname.get("1.0","end-1c")
                nameinputlabel2.config(text = "Name is now: " + requestitem.name)
            def get_manufacturer_input():
                requestitem.manufacturer=inputmanufactuer.get("1.0","end-1c")
                manufactuerinputlabel2.config(text = "Email is now: " + requestitem.manufacturer)
            def get_sku_input():
                requestitem.SKU=inputsku.get("1.0","end-1c")
                skuinputlabel2.config(text = "Shipping Address is now: " + requestitem.SKU)
            def get_release_input():
                requestitem.release=inputrelease.get("1.0","end-1c") 
                releaseinputlabel2.config(text = "Billing Address is now: " + requestitem.release)
            def get_desiredprice_input():
                requestitem.desiredprice=inputdesiredprice.get("1.0","end-1c")
                desiredpriceinputlabel2.config(text = "CCfile Location is now: " + requestitem.desiredprice)
            def get_maxprice_input():
                requestitem.maxprice=inputmaxprice.get("1.0","end-1c")
                maxpriceinputlabel2.config(text = "Spendlimit is now: " + requestitem.maxprice)
            def confirm_request():
                self.requesteditems.append(requestitem)
                createrequestlabel.config(text = "Request Confirmed!")



            window = tk.Toplevel(self.root) #Create new window and base it off orginal window
            window.configure(background="#666666") #Set background color
            window.geometry("676x856") #Set size of window
            label = Label(window, text='Creating a new request', font=("Arial", 15), fg='white', bg='#666666', height=2, width=20)
            label.place(relx=0.5, rely=0, anchor=N)
            separator1 = ttk.Separator(window, orient='horizontal') # Create Horizontal seperator bar
            separator1.place(relx=0, rely=0.04, relwidth=1, relheight=0.005)
            separator2 = ttk.Separator(window, orient='vertical') # Create vertical seperator bar
            separator2.place(relx=0.05, rely=0.04, relwidth=0.005, relheight=1)

            print ("Name is now: " + requestitem.name)
            print("Manufacturer is now: " + requestitem.manufacturer)
            print("SKU is now: " + requestitem.SKU)
            print("Release is now: " + requestitem.release)
            print("Desiredprice is now: " + requestitem.desiredprice)
            print("Maxprice is now: " + requestitem.maxprice)

            nameinputlabel = Label(window, text='Name', font=("Arial", 10), fg='white', bg='#666666', height=2, width=8)
            nameinputlabel.place(relx=0.08, rely=0.1)
            inputname = tk.Text(window, height = 2, width = 40)
            inputname.place(relx=0.4, rely=0.1)
            enterbutton = tk.Button(window, text = "_/", command =lambda: get_name_input())
            enterbutton.place(relx=0.9, rely=0.1)
            nameinputlabel2 = Label(window, text='', font=("Arial", 10), fg='white', bg='#666666', height=2, width=20)
            nameinputlabel2.place(relx=0.35, rely=0.15)

            manufactuerinputlabel = Label(window, text='Manufactuer', font=("Arial", 10), fg='white', bg='#666666', height=2, width=8)
            manufactuerinputlabel.place(relx=0.08, rely=0.2)
            inputmanufactuer = tk.Text(window, height = 2, width = 40)
            inputmanufactuer.place(relx=0.4, rely=0.2)
            enterbutton2 = tk.Button(window, text = "_/", command =lambda: get_manufacturer_input())
            enterbutton2.place(relx=0.9, rely=0.2)
            manufactuerinputlabel2 = Label(window, text='', font=("Arial", 10), fg='white', bg='#666666', height=2, width=20)
            manufactuerinputlabel2.place(relx=0.35, rely=0.25)

            skuinputlabel = Label(window, text='SKU', font=("Arial", 10), fg='white', bg='#666666', height=2, width=14)
            skuinputlabel.place(relx=0.1, rely=0.3)
            inputsku = tk.Text(window, height = 2, width = 40)
            inputsku.place(relx=0.4, rely=0.3)
            enterbutton3 = tk.Button(window, text = "_/", command =lambda: get_sku_input())
            enterbutton3.place(relx=0.9, rely=0.3)
            skuinputlabel2 = Label(window, text='', font=("Arial", 10), fg='white', bg='#666666', height=2, width=20)
            skuinputlabel2.place(relx=0.45, rely=0.35)

            releaseinputlabel = Label(window, text='Release Date', font=("Arial", 10), fg='white', bg='#666666', height=2, width=14)
            releaseinputlabel.place(relx=0.09, rely=0.4)
            inputrelease = tk.Text(window, height = 2, width = 40)
            inputrelease.place(relx=0.4, rely=0.4)
            enterbutton4 = tk.Button(window, text = "_/", command =lambda: get_release_input())
            enterbutton4.place(relx=0.9, rely=0.4)
            releaseinputlabel2 = Label(window, text='', font=("Arial", 10), fg='white', bg='#666666', height=2, width=20)
            releaseinputlabel2.place(relx=0.45, rely=0.45)

            desiredpriceinputlabel = Label(window, text='Desired Price', font=("Arial", 10), fg='white', bg='#666666', height=2, width=14)
            desiredpriceinputlabel.place(relx=0.09, rely=0.5)
            inputdesiredprice = tk.Text(window, height = 2, width = 40)
            inputdesiredprice.place(relx=0.4, rely=0.5)
            enterbutton5 = tk.Button(window, text = "_/", command =lambda: get_desiredprice_input())
            enterbutton5.place(relx=0.9, rely=0.5)
            desiredpriceinputlabel2 = Label(window, text='', font=("Arial", 10), fg='white', bg='#666666', height=2, width=20)
            desiredpriceinputlabel2.place(relx=0.45, rely=0.55)

            maxpriceinputlabel = Label(window, text='Max Price', font=("Arial", 10), fg='white', bg='#666666', height=2, width=14)
            maxpriceinputlabel.place(relx=0.09, rely=0.6)
            inputmaxprice = tk.Text(window, height = 2, width = 40)
            inputmaxprice.place(relx=0.4, rely=0.6)
            enterbutton5 = tk.Button(window, text = "_/", command =lambda: get_maxprice_input())
            enterbutton5.place(relx=0.9, rely=0.6)
            maxpriceinputlabel2 = Label(window, text='', font=("Arial", 10), fg='white', bg='#666666', height=2, width=20)
            maxpriceinputlabel2.place(relx=0.35, rely=0.65)
            
            createrequest = tk.Button(window, text = "Create Request", command =lambda: confirm_request())
            createrequest.place(relx=0.09, rely=0.7)
            createrequestlabel = Label(window, text='', font=("Arial", 10), fg='white', bg='#666666', height=2, width=20)
            createrequestlabel.place(relx=0.35, rely=0.7)
    
    #Function to create the "Cancel Request" Window
    def cancel_request(self): 
        if self.giveninfo == "False":
            self.error_window() #Open up error gui window
        else: 
            window = tk.Toplevel(self.root) #Create new window and base it off orginal window
            window.configure(background="#666666") #Set background color
            window.geometry("676x856") #Set size of window
            label = Label(window, text='Cancelling a request', font=("Arial", 15), fg='white', bg='#666666', height=2, width=20)
            label.place(relx=0.5, rely=0, anchor=N)
            separator1 = ttk.Separator(window, orient='horizontal') # Create Horizontal seperator bar
            separator1.place(relx=0, rely=0.04, relwidth=1, relheight=0.005)
            separator2 = ttk.Separator(window, orient='vertical') # Create vertical seperator bar
            separator2.place(relx=0.05, rely=0.04, relwidth=0.005, relheight=1)
    
    #Function to create the "Input Information" Window
    def input_information(self): 
        def get_name_input():
            self.name=inputname.get("1.0","end-1c")
            nameinputlabel2.config(text = "Name is now: " + self.name)
        def get_email_input():
            self.email=inputemail.get("1.0","end-1c")
            emailinputlabel2.config(text = "Email is now: " + self.email)
        def get_saddr_input():
            self.saddr=inputsaddr.get("1.0","end-1c")
            saddrinputlabel2.config(text = "Shipping Address is now: " + self.saddr)
        def get_baddr_input():
            self.baddr=inputbaddr.get("1.0","end-1c") 
            baddrinputlabel2.config(text = "Billing Address is now: " + self.baddr)
        def get_ccfile_input():
            self.ccfile=inputccfile.get("1.0","end-1c")
            ccfileinputlabel2.config(text = "CCfile Location is now: " + self.ccfile)
        def get_spendlimit_input():
            self.spendlimit=inputspendlimit.get("1.0","end-1c")
            spendlimitinputlabel2.config(text = "Spendlimit is now: " + self.spendlimit)
        def confirm_request():
            UserDatafile = open("userdata.txt", "w") 
            UserData = [self.name, '\n', self.email, '\n', self.saddr, '\n', self.baddr, '\n', self.ccfile, '\n', self.spendlimit, '\n']
            UserDatafile.writelines(UserData)
            UserDatafile.close()
            confirmlabel.config(text = "Information Saved")
            self.giveninfo = "True"

        print ("Name is now: " + self.name)
        print("Email is now: " + self.email)
        print("Shipping Address is now: " + self.saddr)
        print("Billing Address is now: " + self.baddr)
        print("CCfile Location is now: " + self.ccfile)
        print("Spendlimit is now: " + self.spendlimit)

        window = tk.Toplevel(self.root) #Create new window and base it off orginal window
        window.configure(background="#666666") #Set background color
        window.geometry("676x856") #Set size of window
        label = Label(window, text='Inputting user information', font=("Arial", 15), fg='white', bg='#666666', height=2, width=20)
        label.place(relx=0.5, rely=0, anchor=N)
        separator1 = ttk.Separator(window, orient='horizontal') # Create Horizontal seperator bar
        separator1.place(relx=0, rely=0.04, relwidth=1, relheight=0.005)
        separator2 = ttk.Separator(window, orient='vertical') # Create vertical seperator bar
        separator2.place(relx=0.05, rely=0.04, relwidth=0.005, relheight=1)

        nameinputlabel = Label(window, text='Name', font=("Arial", 10), fg='white', bg='#666666', height=2, width=8)
        nameinputlabel.place(relx=0.08, rely=0.1)
        inputname = tk.Text(window, height = 2, width = 40)
        inputname.place(relx=0.4, rely=0.1)
        enterbutton = tk.Button(window, text = "_/", command =lambda: get_name_input())
        enterbutton.place(relx=0.9, rely=0.1)
        nameinputlabel2 = Label(window, text='', font=("Arial", 10), fg='white', bg='#666666', height=2, width=20)
        nameinputlabel2.place(relx=0.35, rely=0.15)

        emailinputlabel = Label(window, text='Email', font=("Arial", 10), fg='white', bg='#666666', height=2, width=8)
        emailinputlabel.place(relx=0.08, rely=0.2)
        inputemail = tk.Text(window, height = 2, width = 40)
        inputemail.place(relx=0.4, rely=0.2)
        enterbutton2 = tk.Button(window, text = "_/", command =lambda: get_email_input())
        enterbutton2.place(relx=0.9, rely=0.2)
        emailinputlabel2 = Label(window, text='', font=("Arial", 10), fg='white', bg='#666666', height=2, width=20)
        emailinputlabel2.place(relx=0.35, rely=0.25)

        saddrinputlabel = Label(window, text='Shipping Address', font=("Arial", 10), fg='white', bg='#666666', height=2, width=14)
        saddrinputlabel.place(relx=0.1, rely=0.3)
        inputsaddr = tk.Text(window, height = 2, width = 40)
        inputsaddr.place(relx=0.4, rely=0.3)
        enterbutton3 = tk.Button(window, text = "_/", command =lambda: get_saddr_input())
        enterbutton3.place(relx=0.9, rely=0.3)
        saddrinputlabel2 = Label(window, text='', font=("Arial", 10), fg='white', bg='#666666', height=2, width=20)
        saddrinputlabel2.place(relx=0.45, rely=0.35)

        baddrinputlabel = Label(window, text='Billing Address', font=("Arial", 10), fg='white', bg='#666666', height=2, width=14)
        baddrinputlabel.place(relx=0.09, rely=0.4)
        inputbaddr = tk.Text(window, height = 2, width = 40)
        inputbaddr.place(relx=0.4, rely=0.4)
        enterbutton4 = tk.Button(window, text = "_/", command =lambda: get_baddr_input())
        enterbutton4.place(relx=0.9, rely=0.4)
        baddrinputlabel2 = Label(window, text='', font=("Arial", 10), fg='white', bg='#666666', height=2, width=20)
        baddrinputlabel2.place(relx=0.45, rely=0.45)

        ccfileinputlabel = Label(window, text='CCfile Location', font=("Arial", 10), fg='white', bg='#666666', height=2, width=14)
        ccfileinputlabel.place(relx=0.09, rely=0.5)
        inputccfile = tk.Text(window, height = 2, width = 40)
        inputccfile.place(relx=0.4, rely=0.5)
        enterbutton5 = tk.Button(window, text = "_/", command =lambda: get_ccfile_input())
        enterbutton5.place(relx=0.9, rely=0.5)
        ccfileinputlabel2 = Label(window, text='', font=("Arial", 10), fg='white', bg='#666666', height=2, width=20)
        ccfileinputlabel2.place(relx=0.45, rely=0.55)

        spendlimitinputlabel = Label(window, text='24hr Spendlimit', font=("Arial", 10), fg='white', bg='#666666', height=2, width=14)
        spendlimitinputlabel.place(relx=0.09, rely=0.6)
        inputspendlimit = tk.Text(window, height = 2, width = 40)
        inputspendlimit.place(relx=0.4, rely=0.6)
        enterbutton5 = tk.Button(window, text = "_/", command =lambda: get_spendlimit_input())
        enterbutton5.place(relx=0.9, rely=0.6)
        spendlimitinputlabel2 = Label(window, text='', font=("Arial", 10), fg='white', bg='#666666', height=2, width=20)
        spendlimitinputlabel2.place(relx=0.35, rely=0.65)

        confirm = tk.Button(window, text = "Confirm Information", command =lambda: confirm_request())
        confirm.place(relx=0.09, rely=0.7)
        confirmlabel = Label(window, text='', font=("Arial", 10), fg='white', bg='#666666', height=2, width=20)
        confirmlabel.place(relx=0.35, rely=0.7)

     #Function to create the "Settings" Window
    def settings(self): 
        window = tk.Toplevel(self.root) #Create new window and base it off orginal window
        window.configure(background="#666666") #Set background color
        window.geometry("676x856") #Set size of window
        label = Label(window, text='Settings', font=("Arial", 15), fg='white', bg='#666666', height=2, width=20)
        label.place(relx=0.5, rely=0, anchor=N)
        separator1 = ttk.Separator(window, orient='horizontal') # Create Horizontal seperator bar
        separator1.place(relx=0, rely=0.04, relwidth=1, relheight=0.005)
        separator2 = ttk.Separator(window, orient='vertical') # Create vertical seperator bar
        separator2.place(relx=0.05, rely=0.04, relwidth=0.005, relheight=1)

    #Function to pop up the Error window when a user is somewhere they should not be
    def error_window(self): 
        window = tk.Toplevel(self.root) #Create new window and base it off orginal window
        window.configure(background="#666666") #Set background color
        window.geometry("676x856") #Set size of window
        label = Label(window, text='Error', font=("Arial", 15), fg='white', bg='#666666', height=2, width=20)
        label.place(relx=0.5, rely=0, anchor=N)
        separator1 = ttk.Separator(window, orient='horizontal') # Create Horizontal seperator bar
        separator1.place(relx=0, rely=0.04, relwidth=1, relheight=0.005)
        separator2 = ttk.Separator(window, orient='vertical') # Create vertical seperator bar
        separator2.place(relx=0.05, rely=0.04, relwidth=0.005, relheight=1)
        errorlabel = Label(window, text='', font=("Arial", 10), fg='white', bg='#666666', height=2, width=50)
        errorlabel.place(relx=0.1, rely=0.1)
        if self.giveninfo == "False":
            errorlabel.config(text = "You must input your information first")
        else:
            errorlabel.config(text = "An Unknown error has occured")
    
    # def exit_handler(self):
    #     print("Name is now" + self.name)
    #     UserDatafile = open("userdata.txt", "w") 
    #     UserData = [self.name, '\n', self.email, '\n', self.saddr, '\n', self.baddr, '\n', self.ccfile, '\n', self.spendlimit, '\n']
    #     UserDatafile.writelines(UserData)
    #     UserDatafile.close()
    #     print ('My application is ending!')
    
# Main of program, creates main window that pops up when program opns 
if __name__ == "__main__":

    # create a root window
    gui = interface()
    
    # def move_window(event):
    #     gui.root.geometry('+{0}+{1}'.format(event.x_root, event.y_root))

    current_theme = 'default'
    background_colo = "#321325"
    main_colo = "#5F0F40"
    accent_colo = "#9A031E"
    text_colo = "#CB793A"
    accent2_colo = "#FCDC4D"
    dull_black = "#000000"
    

    gui.root.configure(background=background_colo)
 
    gui.root.title("Quad-P")

    screen_width= gui.root.winfo_screenwidth()               
    screen_height= gui.root.winfo_screenheight()               
    gui.root.geometry("%dx%d" % (screen_width, screen_height))

    #Create Title at top of main window
    # program_title = Label(gui.root, text='Pothole predictor and pruner program', font=("Verdana", 15), fg=text_colo, bg=main_colo, height=2, width=round(screen_width*0.1))
    # program_title.place(relx=0.5, rely=0, anchor=N)
    # program_title.grid(column=0, row=0)

    # buf_label0 = Label(gui.root, fg=background_colo, bg=background_colo, height=round(screen_height*0.00125), width=round(screen_width*0.059))
    

    # side_data_label = Label(gui.root, fg=main_colo, bg=main_colo, height=round(screen_height*0.0225), width=round(screen_width*0.05555))
    # side_data_label.grid(column=1, row=1)

    video_label = Label(gui.root, fg=dull_black, bg=dull_black, height=round(screen_height*0.0215), width=round(screen_width*0.03555), borderwidth=5, relief="sunken")


    bottom_data_label = Label(gui.root, fg=main_colo, bg=main_colo, height=round(screen_height*0.0555), width=round(screen_width*0.059), borderwidth=5, relief="solid")
    
    #video_label.place(relx=0.025, rely=0.05)

    # Make main menu bar
    menubar = Menu(gui.root, background=main_colo, fg=text_colo, borderwidth=5, relief="solid")
    # menubar.place(relx=0.025, rely=0.05)
    # Declare file and edit for showing in menubar
    file = Menu(menubar, tearoff=False, fg=text_colo, background=main_colo)
    view = Menu(menubar, tearoff=False, fg=text_colo, background=main_colo)
    edit = Menu(menubar, tearoff=False, fg=text_colo, background=main_colo)
    help = Menu(menubar, tearoff=False, fg=text_colo, background=main_colo)
    
    # Add commands in in file menu
    file.add_command(label="New")
    file.add_command(label="Open")
    file.add_command(label="Save")
    file.add_command(label="Save As")
    file.add_command(label="Upload")
    file.add_separator()
    file.add_command(label="Exit", command=gui.root.quit)
    
    # Add commands in view menu
    view.add_command(label="Fullscreen")
    view.add_separator()
    view.add_command(label="Theme")
    
    # Add commands in edit menu
    edit.add_command(label="Cut")
    edit.add_command(label="Copy")
    edit.add_command(label="Paste")
    edit.add_command(label="Scan")
    edit.add_separator()
    edit.add_command(label="M Density")

    # Add commands in help menu
    help.add_command(label="About")
    help.add_command(label="Docs")
    help.add_command(label="Diagnostics")
    help.add_separator()
    help.add_command(label="Developer")
    
    # Display the file and edit declared in previous step
    menubar.add_cascade(label="File", menu=file)
    menubar.add_cascade(label="View", menu=view)
    menubar.add_cascade(label="Edit", menu=edit)
    menubar.add_cascade(label="Help", menu=help)
    
    # Displaying of menubar in the app
    
    gui.root.config(menu=menubar)
    

    # buf_label0.grid(column=0, row=0, columnspan=10)
    video_label.grid(column=0, row=1, columnspan=10, pady = 35, ipadx=5, ipady=5)
    bottom_data_label.grid(column=0, row=2, columnspan=10, pady = 35, ipadx=5, ipady=5, sticky=SW)
    #Loop the main
    gui.root.mainloop()