# External Libraries
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from apscheduler.schedulers.background import BackgroundScheduler
from enum import Enum

# Internal Libraries
from computervision import getUserInput, CVInput, cap, cv2
from store import savedRecipes, getSavedRecipes
from models import Recipe

app = Flask(__name__)
bootstrap = Bootstrap(app)

class AppPages(Enum):
    HOME = "home"
    INPUTINGREDIENTS = "input-ingredients"
    INPUTINSTRUCTIONS = "input-instructions"
    LISTINGREDIENTS = "list-ingredients"
    LISTINSTRUCTIONS = "list-instructions"
    SAVE = "SAVE"
    SELECTSAVED = "select-saved"


PAGETOINPUTMAP = {
    AppPages.HOME: [CVInput.INDEX, CVInput.MIDDLE, CVInput.PINKY, CVInput.PINCH],
    AppPages.INPUTINGREDIENTS: [],
    AppPages.INPUTINSTRUCTIONS: [],
    AppPages.LISTINGREDIENTS: [CVInput.INDEX, CVInput.MIDDLE, CVInput.PINKY, CVInput.PINCH],
    AppPages.LISTINSTRUCTIONS: [CVInput.INDEX, CVInput.MIDDLE, CVInput.PINKY, CVInput.PINCH],
    AppPages.SAVE: [CVInput.INDEX],
    AppPages.SELECTSAVED: [CVInput.INDEX, CVInput.MIDDLE, CVInput.PINKY]
}

class AppState:
    def __init__(self, currentRecipe, currentPage, currentListIndex):
        self.currentRecipe = currentRecipe
        self.currentPage = currentPage
        self.currentListIndex = currentListIndex
    def isCVInputPage(self):
        return False
    
appState = AppState(Recipe('', [], []), AppPages.HOME, 0)


currentRecipe = Recipe('', [], [])
currentIndex = 0

# Get Input
def trackGestures():
    print('tracking gestures')
    return

# Setup Cron Job to Get Input from Webcam
sched = BackgroundScheduler(daemon=True)
sched.add_job(trackGestures,'interval',seconds=5)
sched.start()

# Pages
@app.route('/')
async def home():
    userInput = getUserInput([CVInput.INDEX, CVInput.MIDDLE, CVInput.PINKY])
    print('Got user input lol')
    if userInput == CVInput.INDEX:
        redirect('input/inputting=ingredients&saving=False')
    elif userInput == CVInput.MIDDLE:
        redirect('chooseSaved')
    elif userInput == CVInput.PINKY:
        redirect('save')

    return render_template('home.html')

@app.route('/input', methods =["GET", "POST"])
async def inputPage():
    inputting = request.args.get('inputting')
    saving = request.args.get('saving')

    if request.method == "POST":
        userInput = request.form.get("input")

        inputList = userInput.splitlines();
        for line in inputList:
            if inputting == 'ingredients':
                currentRecipe.ingredients.append(line)
                redirect('input?inputting=instructions')
            elif inputting == 'instructions':
                currentRecipe.instructions.append(line)

                if saving:
                    redirect('save')
                else:
                    redirect('/list?displaying=ingredients')

    return render_template('input.html', formLabel = inputting)

@app.route('/list')
async def listPage():
    displaying = request.args.get('displaying')
    
    allItems = currentRecipe.ingredients if displaying == 'ingredients' else currentRecipe.instructions
 
    global currentIndex
    itemsToRender = []
    itemsToRender.append(allItems[currentIndex]);

    userInput = None
    userInput = getUserInput([CVInput.INDEX, CVInput.MIDDLE, CVInput.PINKY, CVInput.PINCH])
    if not(userInput == None):
        currentIndex = currentIndex + 1

        if currentIndex > len(allItems) - 1:
            if displaying == 'ingredients':
                redirect('/list?displaying=instructions')
            elif displaying == 'instructions':
                redirect('save')
                

        itemsToRender.append(allItems[currentIndex])

    return render_template('list.html', itemsToRender, currentIndex = currentIndex,)



if __name__ == '__main__':
   getSavedRecipes()
   app.run()

   #Closing the app
   cap.release()
   cv2.destroyAllWindows()