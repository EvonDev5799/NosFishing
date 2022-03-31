#image manipulation
from PIL import ImageGrab
import cv2

# input simulation
import keyboard
import mouse

import tkinter as tk	# windowing
import numpy as np		# computations
from time import sleep	# waiting
import random			# shuffling

#INFO about the script
__author__ 	= "Evonis"
__credits__ = ["Netherarmy"]
__version__ = "2 Beta"
__status__ = "Beta"

# GOBAL VARIABLES

# for dictionary and other things
keys = ("right", "up", "left", "down") # list of the key names

# for listeners
StopKey	= "0"	# global var for the stopping key

# Functions

# picture dictionary initializers

def InitArrows():
	return {
		keys[0] : cv2.imread("sprites\\arrowRight.png", 0)	,
		keys[1] : cv2.imread("sprites\\arrowUp.png", 0)		,
		keys[2] : cv2.imread("sprites\\arrowLeft.png", 0)	,
		keys[3] : cv2.imread("sprites\\arrowDown.png", 0)
	}

def InitRods():
	return {
		keys[0] : cv2.imread("sprites\\rodRight.png", 0)	,
		keys[1] : cv2.imread("sprites\\rodUp.png", 0)		,
		keys[2] : cv2.imread("sprites\\rodLeft.png", 0)		,
		keys[3] : cv2.imread("sprites\\rodDown.png", 0)
	}

def InitSteps():
	return {
		"0window"		: cv2.imread("sprites\\window.png", 0)		,
		"1start"		: cv2.imread("sprites\\gameStart.png", 0)	,
		"2getReward"	: cv2.imread("sprites\\getReward.png", 0)	,
		"2retry"		: cv2.imread("sprites\\retry.png", 0)		,
		"3box1"			: cv2.imread("sprites\\dark1.png", 0)		,
		"3box2"			: cv2.imread("sprites\\dark2.png", 0)		,
		"3box3"			: cv2.imread("sprites\\dark3.png", 0)		,
		"3box4"			: cv2.imread("sprites\\dark4.png", 0)		,
		"3box5"			: cv2.imread("sprites\\dark5.png", 0)		,
		"4playAgain"	: cv2.imread("sprites\\playAgain.png", 0)
	}

def InitTargets():
	return {
		"fake"	: cv2.imread("sprites\\fake_end.png", 0),
		"real"	: cv2.imread("sprites\\end.png", 0)
	}

def InitImages():
	return {
		"arrows"	: InitArrows()	,
		"rods"		: InitRods()	,
		"steps"		: InitSteps()	,
		"targets"	: InitTargets()
	}

# Listener

def StopListener():
	return keyboard.is_pressed(StopKey)

# Functions for Image Treatment

def ScreenShot(window = None):
	img_rgb = np.array(ImageGrab.grab(window))
	img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
	return img_gray

def ImageSearch(image, window=None, precision=0.9):
    screen = ScreenShot(window)
    y, x = image.shape
    res = cv2.matchTemplate(screen, image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val < precision:
        return None
    return [max_loc[0], max_loc[1], max_loc[0] + x, max_loc[1] + y]

def IsOnScreen(image, screen, precision=0.95):
	res = cv2.matchTemplate(screen, image, cv2.TM_CCOEFF_NORMED)
	min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
	if max_val < precision:
		return False
	return True

# Click Management

def ClicksOnCoordinates(x, y, delay= 0):
	mouse.move(x, y)
	sleep(delay)
	mouse.click()

def ClickOnImage(image, precision=0.95,  delay = 0):
	rect = ImageSearch(image, precision = precision)
	if rect == None:
		return None
	ClicksOnCoordinates( (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2, delay)
	return rect

def WaitClickImage(image, precision=0.95, delay = 0):
	while ClickOnImage(image, precision, delay) == None:
		if StopListener():
			return False
	return True

# Randomness

def GameSequence(wins, losses):
	sequence = ["fake"]*losses + ["real"]*wins
	random.shuffle(sequence)
	return sequence

# Gaming Functions

def HighscoreScan(screen, target):
		return IsOnScreen(target, screen, 0.9)


def arrowsOnScreen(screen, arrows):
	for key in keys:
		if IsOnScreen(arrows[key], screen):	
			return True

def QteScan(screen, arrows):
	for key in keys:
		if IsOnScreen(arrows[key], screen):		
			keyboard.press_and_release(key)
			sleep(0.1)
			return True
	return False

def RodScan(screen, rods):
	for key in keys:
			if IsOnScreen(rods[key], screen):
				keyboard.press_and_release(key)

def Play(target, window, arrows, rods): #return the won state
	memory = False
	while True: # Playing Loop

		# Interrupting Feature
		if StopListener():
			return False

		# Scans
		screen = ScreenShot(window)

		if HighscoreScan(screen, target):
			return True

		if arrowsOnScreen(screen, arrows):
			if memory:
				QteScan(screen, arrows)
			else:
				sleep(0.1)
			memory = True
		else:
			memory = False
			RodScan(screen, rods)		

# Windowing Functions


def getEntryData(entries):

	return int(entries[0].get()), int(entries[1].get()), int(entries[2].get())

def RunCommand(images, settings):

	images	= InitImages()

	SuccessQuantity, FailQuantity, AutoLootLevel = settings

	window = None
	sequence = GameSequence(SuccessQuantity, FailQuantity)

	while window == None:
		if StopListener():
			return
		window = ImageSearch(images["steps"]["0window"])

	if AutoLootLevel == 0:
		Play(images["targets"]["real"], window, images["arrows"], images["rods"])
		return
	else:
		for game in sequence:
			if not WaitClickImage(images["steps"]["1start"], delay=1):
				return
			
			target = images["targets"][game]
			if not Play(target, window, images["arrows"], images["rods"]):
				return
			
			if game == "real":
				if not WaitClickImage(images["steps"]["2getReward"], delay=1):
					return

				stepName = "3box" + str(AutoLootLevel)
				if not WaitClickImage(images["steps"][stepName], delay=1):
					return
				if not WaitClickImage(images["steps"]["4playAgain"], delay=1):
					return
			elif game == "fake":
				if not WaitClickImage(images["steps"]["2retry"], delay=1):
					return

	


def InitWindow(images):
	root = tk.Tk()
	root.title("NosFishing " + __version__)
	root.wm_iconbitmap('NF.ico')
	# Position (0;0) : Label for Success Quantity
	tk.Label(root, text = "Success Quantity (how many good scores, 20k+)").grid(row=0)
	# Position (1;0) : Label for Success Quantity
	tk.Label(root, text = "Fail Quantity (how many bad scores, 10k+)").grid(row=1)
	# Position (2;0) : Label for AutoLootLevel
	tk.Label(root, text = "AutoLootLevel (the reward level from 1 to 5, put 0 for manual looting)").grid(row=2)

	# Position (0;1) : Entry for Succes Quantity
	e1 = tk.Entry(root)
	e1.grid(row=0, column=1)
	# Position (1;1) : Entry for Fail Quantity
	e2 = tk.Entry(root)
	e2.grid(row=1, column=1)
	# Position (2;1) : Entry for Auto Loot Level
	e3 = tk.Entry(root)
	e3.grid(row=2, column=1)

	entries = (e1, e2, e3)

	tk.Button(
		root, 
		text='Quit', 
		command=root.quit).grid(
			row=3, 
			column=0, 
			sticky=tk.W, 
			pady=4)

	tk.Button(
		root, 
		text='Run', command= lambda: RunCommand(images, getEntryData(entries))).grid(
			row=3, 
			column=1, 
			sticky=tk.W, 
			pady=4)
		
	return root

def main():
	images	= InitImages()

	root = InitWindow(images)

	root.mainloop()

main()