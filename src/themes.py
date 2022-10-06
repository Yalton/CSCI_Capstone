############################################################
# themes.py 
# Used to store gui themes 
############################################################
# Creation Date 9/7/22
# Author: Dalton Bailey
# Course: CSCI 490
# Instructor Sam Siewert
############################################################
themes = {}
themeidict = {}
default = {}
spicy = {}
juicy = {}

# Define default theme
default['background_colo'] = "#321325"
default['main_colo'] = "#5F0F40"
default['accent_colo'] = "#9A031E"
default['text_colo'] = "#CB793A"
default['accent2_colo'] = "#FCDC4D"

# Define spicy theme
spicy['background_colo'] = "#BF3100"
spicy['main_colo'] = "#D76A03"
spicy['accent_colo'] = "#EC9F05"
spicy['text_colo'] = "#000000"
spicy['accent2_colo'] = "#F5BB00"

# Define spicy theme
juicy['background_colo'] = "#2A4747"
juicy['main_colo'] = "#439775"
juicy['accent_colo'] = "#48BF84"
juicy['text_colo'] = "#E0BAD7"
juicy['accent2_colo'] = "#61D095"


# Define other themes theme

# Populate theme variable with theme set
themes['default'] = default
themes['spicy'] = spicy
themes['juicy'] = juicy
themeidict[1] = 'default'
themeidict[2] = 'spicy'
themeidict[3] = 'juicy'
