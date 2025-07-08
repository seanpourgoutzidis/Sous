import time
import os
import datetime


ingredients = instructions = []
intraRecipeDelimeter = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
interRecipeDelimeter = '========================================================'

class Recipe:
    def __init__(self, name, ingredients, instructions):
        self.name = name
        self.ingredients = ingredients
        self.instructions = instructions

savedRecipes = []


#TODO - Use a closure to validate input



def displayInstructions():
	print('---------------------------------')
	print('Press A: Quick Start Recipe')
	print('Press B: Select from Existing Recipes')
	print('Press C: Add a new recipe')
	print('Press Q: Quit Program')

	validOptions = ['a', 'b', 'c', 'q']
 
	while True:
		userInput = input("Enter option above:\n")
		if (userInput.lower() in validOptions):
			return userInput

		print("Invalid input, try again")

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

	while True:
		saveRecipeInput = input('Would you like to save this recipe? (Y/N): ')

		if (saveRecipeInput.lower() == 'y'):
			saveRecipe(True)
			break
		elif (saveRecipe.lower == 'n'):
			break
		else:
			print("Invalid input, try again")

	input("\nPress enter to continue")
	os.system('clear')


def setTimer():
	hours = int(input('Enter hours: '))
	minutes = int(input('Enter minutes: '))
	seconds = int(input('Enter seconds: '))

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
		_ = input(item)
		if ("minute" in item or "hour" in item):
			userInput = input("Would you like to set a timer? (Y/N)")

			if(userInput.lower() == 'y'):
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

			userInput = input('Would you like to try again? (Y/N): ')

			if (userInput.lower() == 'n'):
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
	input("\nPress enter to continue")
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

	recipeIndex = 0

	while True:
		recipeIndex = input('Enter the number of the recipe you would like to make: ')

		if (recipeIndex.isdigit() and int(recipeIndex) < index and int(recipeIndex) > 0):
			break

		print("Invalid input, try again")

	recipe = savedRecipes[int(recipeIndex) - 1]
	playRecipe(recipe.ingredients, recipe.instructions)



# Entry Point
if __name__ == "__main__":

	print("Welcome to Sous!")

	while True:
		choiceMode = displayInstructions()

		match choiceMode:
			case 'a':
				quickStartRecipe()
			case 'b':
				chooseSavedRecipes()
			case 'c':
				saveRecipe()
			case 'q':
				print('\n\nThank you for using sous! :)')



	


	


	