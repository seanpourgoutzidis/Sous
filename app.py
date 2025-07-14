# External Libraries
from flask import Flask, render_template, redirect, url_for, request, flash, current_app
from flask_bootstrap import Bootstrap
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import requests
from blinker import Namespace, signal
from flask_socketio import SocketIO, emit

# Internal Libraries
from computervision import getUserInput, CVInput, cap, cv2
from store import savedRecipes, getSavedRecipes, saveRecipe, isRecipeInDatabase
from models import AppState, Recipe, AppPages, Flows

app = Flask(__name__)
app.config['SECRET_KEY'] = 'oooooooyouwannaguessmesobad'
bootstrap = Bootstrap(app)
socketio = SocketIO(app)

STATE = AppState(Flows.QUICKSTART, Recipe('', [], []), AppPages.HOME, 0, savedRecipes)

def resetState():
    global STATE
    STATE = AppState(Flows.QUICKSTART, Recipe('', [], []), AppPages.HOME, 0, savedRecipes)
    
# Get Input
def trackGestures():
    print('Tracking Gestures')
    global STATE

    newInput = getUserInput()
    print('Input Received - ', newInput)

    if newInput == None:
        return
    
    match STATE.currentPage:
        case AppPages.HOME:
            print('Home')
            if (newInput == CVInput.INDEX):
                STATE.currentFlow = Flows.QUICKSTART
                STATE.currentPage = AppPages.INPUT
                print('redirecting to input')
                socketio.emit('redirect_client', {'url': '/input'})
            elif (newInput == CVInput.MIDDLE):
                STATE.currentFlow = Flows.CHOOSESAVED
                STATE.currentPage = AppPages.SELECTSAVED
                STATE.savedRecipes = getSavedRecipes()
                socketio.emit('redirect_client', {'url': '/select-saved'})
            elif (newInput == CVInput.PINKY):
                STATE.currentFlow = Flows.SAVE
                STATE.currentPage = AppPages.INPUT
                STATE.savedRecipes = getSavedRecipes()
                socketio.emit('redirect_client', {'url': '/input'})
            elif (newInput == CVInput.PINCH):
                exit()
        case AppPages.LISTINGREDIENTS:
            print('Ingredients')
            if (newInput == CVInput.INDEX and STATE.currentListIndex < len(STATE.currentRecipe.ingredients) - 1):
                STATE.currentListIndex = STATE.currentListIndex + 1
                socketio.emit('redirect_client', {'url': '/list?displaying=ingredients'})
            elif (newInput == CVInput.INDEX and STATE.currentListIndex == len(STATE.currentRecipe.ingredients) - 1):
                STATE.currentListIndex = 0
                STATE.currentPage = AppPages.LISTINSTRUCTIONS
                socketio.emit('redirect_client', {'url': '/list?displaying=instructions'})
            elif (newInput == CVInput.PINCH):
                resetState()
                socketio.emit('redirect_client', {'url': '/'})
        case AppPages.LISTINSTRUCTIONS:
            print('Instructions')
            if (newInput == CVInput.INDEX and STATE.currentListIndex < len(STATE.currentRecipe.instructions) - 1):
                STATE.currentListIndex = STATE.currentListIndex + 1
                socketio.emit('redirect_client', {'url': '/list?displaying=instructions'})
            elif (newInput == CVInput.INDEX and STATE.currentListIndex == len(STATE.currentRecipe.instructions) - 1):
                STATE.currentListIndex = 0
                STATE.currentPage = AppPages.SAVEPROMPT
                socketio.emit('redirect_client', {'url': '/save'})
            elif (newInput == CVInput.PINCH):
                resetState()
                socketio.emit('redirect_client', {'url': '/'})
        case AppPages.SAVEPROMPT:
            print('Save Prompt')
            if (newInput == CVInput.INDEX):
                saveRecipe(STATE.currentRecipe)
                STATE.currentPage = AppPages.SAVECONFIRMATION
                socketio.emit('redirect_client', {'url': '/saved-confirmation'})
            elif (newInput == CVInput.MIDDLE):
                resetState()
                STATE.currentPage = AppPages.HOME
                socketio.emit('redirect_client', {'url': '/'})
            elif (newInput == CVInput.PINCH):
                resetState()
                socketio.emit('redirect_client', {'url': '/'})
        case AppPages.SAVECONFIRMATION:
            print('Save Confirmation')
            if (newInput == CVInput.INDEX):
                resetState()
                STATE.currentPage = AppPages.HOME
                socketio.emit('redirect_client', {'url': '/'})
        case AppPages.SELECTSAVED:
            print('Select Saved')
            if (newInput == CVInput.INDEX and STATE.currentListIndex < len(STATE.savedRecipes) - 1):
                STATE.currentListIndex = STATE.currentListIndex + 1
                socketio.emit('redirect_client', {'url': '/select-saved'})
            elif (newInput == CVInput.MIDDLE and STATE.currentListIndex > 0):
                STATE.currentListIndex = STATE.currentListIndex - 1
                socketio.emit('redirect_client', {'url': '/select-saved'})
            elif (newInput == CVInput.PINKY):
                STATE.currentPage = AppPages.LISTINGREDIENTS
                STATE.currentRecipe = STATE.savedRecipes[STATE.currentListIndex]
                STATE.currentListIndex = 0
                socketio.emit('redirect_client', {'url': '/list?displaying=ingredients'})
            elif (newInput == CVInput.PINCH):
                resetState()
                socketio.emit('redirect_client', {'url': '/'})
        case AppPages.INPUT:
            if (newInput == CVInput.PINCH):
                resetState()
                socketio.emit('redirect_client', {'url': '/'})

    print('State after transition - ', STATE)
    return

# Setup Cron Job to Get Input from Webcam
sched = BackgroundScheduler(daemon=True)
sched.add_job(trackGestures,'interval',seconds=5)
sched.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: sched.shutdown())

# Pages
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/input', methods =["GET", "POST"])
def inputPage():

    print('in input')

    if request.method == 'POST':
        recipeNameInput = request.form['name']
        ingredientsInput = request.form['ingredients']
        instructionsInput = request.form['instructions']

        print('Recipe Name - ', recipeNameInput)
        print('Ingredients - ', ingredientsInput)
        print('Instructions - ', instructionsInput)

        if not recipeNameInput or not ingredientsInput or not instructionsInput:
            flash('Error! Make sure all fields are filled')
            print('Error! Make sure all fields are filled')
            return

        ingredients = []
        ingredients = ingredientsInput.splitlines()

        instructions = []
        instructions = instructionsInput.splitlines()
        

        isDup, reason = isRecipeInDatabase(recipeNameInput, ingredients, instructions)
        if isDup:
            flash('Recipe already in database')
            print('Recipe already in database - ', reason)
            resetState()
            return redirect('/')
        
        if STATE.currentFlow == Flows.SAVE:
            saveRecipe(Recipe(recipeNameInput, ingredients, instructions))
            STATE.currentPage = AppPages.SAVECONFIRMATION
            return redirect('/saved-confirmation')
        elif STATE.currentFlow == Flows.QUICKSTART:
            STATE.currentRecipe = Recipe(recipeNameInput, ingredients, instructions)
            STATE.currentPage = AppPages.LISTINGREDIENTS
            return redirect('/list?displaying=ingredients')
            

    print('rendering input template')
    return render_template('input.html')

@app.route('/list')
def listPage():
    displaying = request.args.get('displaying')

    print('Displaying - ', displaying)

    itemsToRender = []

    if (displaying == "ingredients"):
        itemsToRender = STATE.currentRecipe.ingredients[:STATE.currentListIndex + 1]
    elif (displaying == "instructions"):
        itemsToRender = STATE.currentRecipe.instructions[:STATE.currentListIndex + 1]

    print("Items to Render - ", itemsToRender)
    
    return render_template('list.html', listToRender=itemsToRender, pageTitle=displaying, currentIndex=STATE.currentListIndex)

@app.route('/select-saved')
def selectSaved():
    print('Saved Recipes - ', STATE.savedRecipes)
    return render_template('choose-saved.html', listToRender=STATE.savedRecipes, currentIndex=STATE.currentListIndex)

@app.route('/save')
def savePrompt():
    return render_template('save-prompt.html')

@app.route('/saved-confirmation')
def savedConfirmation():
    return render_template('saved-confirmation.html')



if __name__ == '__main__':
   STATE.savedRecipes = getSavedRecipes()
   app.run()
   socketio.run(app)

   #Closing the app
   cap.release()
   cv2.destroyAllWindows()
   sched.shutdown()