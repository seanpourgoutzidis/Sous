# General Function
import time
import os
import datetime
from enum import Enum

# Computer Vision
import cv2
import mediapipe as mp
import pyautogui

# Class Declarations
class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def isZero(self):
    	return self.x == 0 and self.y == 0

class Input(Enum):
	INDEX = 1
	MIDDLE = 2
	PINKY = 3
	PINCH = 4

class Recipe:
    def __init__(self, name, ingredients, instructions):
        self.name = name
        self.ingredients = ingredients
        self.instructions = instructions

# Initialize hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Get screen resolution
screen_width, screen_height = pyautogui.size()

cap = cv2.VideoCapture(0)

# Constant Parameters
THRESHOLD = 100
NEG_THRESHOLD = -100


IndexStates = Coordinate(0,0)
MiddleStates = Coordinate(0,0)
ThumbStates = Coordinate(0,0)
PinkyStates = Coordinate(0,0)
timeOfLastInput = 0

# Recognize different gestures

def IsPinchGesture():
    return not(IndexStates.isZero()) and abs(IndexStates.x - ThumbStates.x) < THRESHOLD / 2 and abs(IndexStates.y - ThumbStates.y) < THRESHOLD / 2 and abs(MiddleStates.x - ThumbStates.x) < THRESHOLD / 2 and abs(MiddleStates.y - ThumbStates.y) < THRESHOLD / 2

def IsIndexTouchingThumb():
    return not(IndexStates.isZero()) and abs(IndexStates.x - ThumbStates.x) < THRESHOLD / 2 and abs(IndexStates.y - ThumbStates.y) < THRESHOLD / 2

def IsMiddleTouchingThumb():
    return not(MiddleStates.isZero()) and abs(MiddleStates.x - ThumbStates.x) < THRESHOLD / 2 and abs(MiddleStates.y - ThumbStates.y) < THRESHOLD / 2

def IsPinkyTouchingThumb():
    return not(PinkyStates.isZero()) and abs(PinkyStates.x - ThumbStates.x) < THRESHOLD / 2 and abs(PinkyStates.y - ThumbStates.y) < THRESHOLD / 2


ingredients = instructions = []
intraRecipeDelimeter = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
interRecipeDelimeter = '========================================================'

savedRecipes = []

def getUserInput(validOptions):

	global IndexStates
	global MiddleStates
	global ThumbStates
	global PinkyStates

	global timeOfLastInput
	timeOfLastInput = time.time()

	while cap.isOpened():
		ret,frame = cap.read()

    	# Flip the frame horizontally
		frame = cv2.flip(frame, 1)

		# Convert to RGB
		rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		results = hands.process(rgb_frame)
	 
		# Check if hand landmarks are available
		if results.multi_hand_landmarks:
			for landmarks in results.multi_hand_landmarks:

	        	# Get the tip of the index finger
				index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
				middle_tip = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
				thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
				pinky_tip = landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

				IndexStates = Coordinate(int(index_tip.x * screen_width), int(index_tip.y * screen_height))
				MiddleStates = Coordinate(int(middle_tip.x * screen_width), int(middle_tip.y * screen_height))
				ThumbStates = Coordinate(int(thumb_tip.x * screen_width), int(thumb_tip.y * screen_height))
				PinkyStates = Coordinate(int(pinky_tip.x * screen_width), int(pinky_tip.y * screen_height))

				timeSinceLastInput = time.time() - timeOfLastInput
				if timeSinceLastInput < 2:
					break
	            
				if (IsPinchGesture() and Input.PINCH in validOptions):
					timeOfLastInput = time.time()
					return Input.PINCH
				elif (IsIndexTouchingThumb() and Input.INDEX in validOptions):
					timeOfLastInput = time.time()
					return Input.INDEX
				elif (IsMiddleTouchingThumb() and Input.MIDDLE in validOptions):
					timeOfLastInput = time.time()
					return Input.MIDDLE
				elif (IsPinkyTouchingThumb() and Input.PINKY in validOptions):
					timeOfLastInput = time.time()
					return Input.PINKY

def displayInstructions():
	print('---------------------------------')
	print('Press A: Quick Start Recipe')
	print('Press B: Select from Existing Recipes')
	print('Press C: Add a new recipe')
	print('Press Q: Quit Program')

	return getUserInput([Input.INDEX, Input.MIDDLE, Input.PINKY, Input.PINCH])

def quickStartRecipe():
	print('Quick Starting Recipe...')
	time.sleep(1)
	os.system('clear')

	print("Enter the list of ingredients: \n")

	global ingredients
	ingredients = []
	while True:
		line = input()
		if line:
			ingredients.append(line)
		else:
			break

	print("Enter the list of instructions: \n")

	global instructions
	instructions = []
	while True:
		line = input()
		if line:
			instructions.append(line)
		else:
			break

	playRecipe(ingredients, instructions)

	print('Would you like to save this recipe? (Index/Middle)')
	usersInput = getUserInput([Input.INDEX, Input.MIDDLE])

	if usersInput == Input.INDEX:
		saveRecipe(True)

	print('Any gesture to continue')
	_ = getUserInput([Input.INDEX, Input.MIDDLE, Input.PINKY, Input.PINCH])
	os.system('clear')


def setTimer():

	hours = 0
	minutes = 0
	seconds = 0

	usersInput = None

	print('Enter hours - index to increment, middle to decrement & pinky to set')
	while not(usersInput == Input.PINKY):
		usersInput = getUserInput([Input.INDEX, Input.MIDDLE, Input.PINKY])

		if usersInput == Input.INDEX:
			hours = hours + 1
			print('hours: ' + str(hours))

		elif usersInput == Input.MIDDLE:
			if hours > 0:
				hours = hours - 1
				print('hours: ' + str(hours))

	print('Hours set to ' + str(hours))
	usersInput = None

	print('Enter minutes - index to increment, middle to decrement & pinky to set')
	while not(usersInput == Input.PINKY):
		usersInput = getUserInput([Input.INDEX, Input.MIDDLE, Input.PINKY])

		if usersInput == Input.INDEX:
			minutes = minutes + 1
			print('minutes: ' + str(minutes))

		elif usersInput == Input.MIDDLE:
			if minutes > 0:
				minutes = minutes - 1
				print('minutes: ' + str(minutes))

	print('Minutes set to ' + str(minutes))
	usersInput = None

	print('Enter seconds - index to increment, middle to decrement & pinky to set')
	while not(usersInput == Input.PINKY):
		usersInput = getUserInput([Input.INDEX, Input.MIDDLE, Input.PINKY])

		if usersInput == Input.INDEX:
			seconds = seconds + 1
			print('seconds: ' + str(seconds))

		elif usersInput == Input.MIDDLE:
			if seconds > 0:
				seconds = seconds - 1
				print('seconds: ' + str(seconds))

	print('Seconds set to ' + str(seconds))

	total_seconds = 3600 * hours + 60 * minutes + seconds

	print('Timer Set! You`ll be notified when it ends')

	while total_seconds > 0:
		timer = datetime.timedelta(seconds = total_seconds)
		time.sleep(1)
		total_seconds -= 1

	print('Timer is done!')
	os.system("say timer done now")
	print("\a\a\a\a\a\a\a\a")


def iterateList(list):
	for item in list:
		print(item)
		_ = getUserInput([Input.INDEX, Input.MIDDLE, Input.PINKY, Input.PINCH])
		if ("minute" in item or "hour" in item):
			print("Would you like to set a timer? (Index/Middle)")
			usersInput = getUserInput([Input.INDEX, Input.MIDDLE])

			if (usersInput == Input.INDEX):
				setTimer()

def playRecipe(ingredients, instructions):
	print("Starting Recipe...")
	time.sleep(1);
	os.system('clear')

	print("Gather Ingredients")
	iterateList(ingredients)
	os.system('clear')

	print("Instructions")
	iterateList(instructions)
	os.system('clear')

	print('Done! Enjoy your food!')

def isRecipeInDatabase(name = '', ingredients = [], instructions = []):
	getSavedRecipes()

	for recipe in savedRecipes:
		if recipe.name == name:
			return True, 'name'
		elif recipe.ingredients == ingredients and recipe.instructions == instructions:
			return True, 'recipe'
	
	return False, ''



def saveRecipe(haveRecipe=False):
	getSavedRecipes()

	recipeName = ''

	while True:
		recipeName = input("Enter the name of the recipe you would like to save: ")

		inDatabase = False
		field = ""

		if (not(haveRecipe)):

			print("Enter the list of ingredients: \n")

			localIngredients = []
			while True:
				line = input()
				if line:
					ingredients.append(line)
				else:
					break

			os.system('clear')

			print("Enter the list of instructions: \n")

			localInstructions = []
			while True:
				line = input()
				if line:
					localInstructions.append(line)
				else:
					break

			inDatabase, field = isRecipeInDatabase(recipeName, localIngredients, localInstructions)
			os.system('clear')
		else:
			inDatabase, field = isRecipeInDatabase(recipeName, ingredients, instructions)
		

		print(field)

		if (inDatabase):
			print(f'Failed to save recipe, {field} already in database')
			print('Would you like to try again? (Index/Middle): ')
			if (getUserInput([Input.INDEX, Input.MIDDLE]) == Input.MIDDLE):
				break
		else:
			break



	# Write to the recipe file to save it
	recipeFile = open('recipes.txt', 'a+')
	recipeFile.write('|' + recipeName + '|')
	recipeFile.write('\n' + intraRecipeDelimeter + '\n')

	for ingredient in ingredients:
		recipeFile.write(ingredient + '\n')

	recipeFile.write(intraRecipeDelimeter + '\n')

	for instruction in instructions:
		recipeFile.write(instruction + '\n')

	recipeFile.write(interRecipeDelimeter + '\n')
	recipeFile.close()

	print('Your recipe has been saved!')
	print("\nAny gesture to continue")
	getUserInput([Input.INDEX, Input.MIDDLE, Input.PINKY, Input.PINCH])
	os.system('clear')

def getSavedRecipes():
	recipeFile = open("recipes.txt")
	recipeText = recipeFile.read()
	recipeFile.close()

	if recipeText == "":
		return

	recipeList = recipeText.split(interRecipeDelimeter)

	global savedRecipes
	savedRecipes = []

	for recipe in recipeList:
		components = recipe.split(intraRecipeDelimeter)

		# If it's whitespace, continue to handle the last line
		if (components[0] == '\n'):
			continue

		name = components[0].replace("|", "")
		localIngredients = components[1].splitlines()
		localInstructions = components[2].splitlines()

		savedRecipes.append(Recipe(name, localIngredients, localInstructions))


def chooseSavedRecipes():
	getSavedRecipes()

	index = 1
	for recipe in savedRecipes:
		print(f"{index}. {recipe.name}")
		index += 1

	recipeIndex = 1
	usersInput = None

	while not(usersInput == Input.PINKY):
		usersInput = getUserInput([Input.INDEX, Input.MIDDLE, Input.PINKY])

		if usersInput == Input.INDEX and recipeIndex < index:
			recipeIndex = recipeIndex + 1
		elif usersInput == Input.MIDDLE and recipeIndex > 0:
			recipeIndex = recipeIndex - 1

		print(f"Current Selection: {recipeIndex}")

	recipe = savedRecipes[int(recipeIndex) - 1]
	playRecipe(recipe.ingredients, recipe.instructions)



# Entry Point
if __name__ == "__main__":

	print("Welcome to Sous!")

	while True:
		usersInput = displayInstructions()

		match usersInput:
			case Input.INDEX:
				quickStartRecipe()
			case Input.MIDDLE:
				chooseSavedRecipes()
			case Input.PINKY:
				saveRecipe()
			case Input.PINCH:
				print('\n\nThank you for using sous! :)')
				break

	cap.release()
	cv2.destroyAllWindows()



	


	


	