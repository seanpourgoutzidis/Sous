from models import Recipe

intraRecipeDelimeter = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
interRecipeDelimeter = '========================================================'

savedRecipes = []

def isRecipeInDatabase(name = '', ingredients = [], instructions = []):
	getSavedRecipes()

	for recipe in savedRecipes:
		if recipe.name == name:
			return True, 'name'
		elif recipe.ingredients == ingredients and recipe.instructions == instructions:
			return True, 'recipe'
	
	return False, ''

def saveRecipe(recipe):
    getSavedRecipes()

    inDatabase, field = isRecipeInDatabase(recipe.name, recipe.ingredients, recipe.instructions)
	
    if inDatabase:
        return True, f'Failed to save recipe, {field} already in database'
	
    # Write to the recipe file to save it
    recipeFile = open('recipes.txt', 'a+')
    recipeFile.write('|' + recipe.name + '|')
    recipeFile.write('\n' + intraRecipeDelimeter + '\n')

    for ingredient in recipe.ingredients:
        recipeFile.write(ingredient + '\n')

    recipeFile.write(intraRecipeDelimeter + '\n')

    for instruction in recipe.instructions:
        recipeFile.write(instruction + '\n')

    recipeFile.write(interRecipeDelimeter + '\n')
    recipeFile.close()
	
    return False, ''

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
