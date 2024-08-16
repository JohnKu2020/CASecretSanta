"""
File: main.py
--------------
Author:  Yevhen K
Date:    16/08/2024

Module Title:	    Python Programming
Assessment Title:   Web API
Description:
A “Secret Santa” program that prompts the user for names and emails of the participants. 
It then emails each participant the person they need to buy a gift for.
"""

from santa import Santa

mySanta = Santa()
users = mySanta.getMembers()
filename = mySanta.save2File(users)
users =mySanta.loadFromFile(filename)
shuffle = mySanta.randomAssignment(users)
mySanta.sendInvitations(shuffle, True)
#mySanta.sortDirectory("C:\\Users\\Admin\\Python","C:\\Users\\Admin\\Python\\sorted","C:\\Users\\Admin\\Python\\misc")