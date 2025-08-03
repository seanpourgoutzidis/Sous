from enum import Enum

# Class Definitions
class AppState:
    def __init__(self, currentFlow, currentRecipe, currentPage, currentListIndex, savedRecipes):
        self.currentFlow = currentFlow
        self.currentRecipe = currentRecipe
        self.currentPage = currentPage
        self.currentListIndex = currentListIndex
        self.savedRecipes = savedRecipes
        self.openedBrowser = False
    def isCVInputPage(self):
        return False

class Recipe:
    def __init__(self, name, ingredients, instructions):
        self.name = name
        self.ingredients = ingredients
        self.instructions = instructions

class AppPages(Enum):
    HOME = "home"
    INPUT = "input"
    LISTINGREDIENTS = "list-ingredients"
    LISTINSTRUCTIONS = "list-instructions"
    SAVEPROMPT = "save-prompt"
    SAVECONFIRMATION = "save-confirmation"
    SELECTSAVED = "select-saved"
    DONE = "done"

class Flows(Enum):
    QUICKSTART = "quickstart"
    CHOOSESAVED = "choose-saved"
    SAVE = "save"