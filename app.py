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
                socketio.emit('redirect_client', {'url': '/input'})
            elif (newInput == CVInput.PINCH):
                exit()
        case AppPages.LISTINGREDIENTS:
            print('Ingredients')
            if (newInput == CVInput.INDEX and STATE.currentListIndex < len(STATE.currentRecipe.ingredients) - 1):
                STATE.currentListIndex = STATE.currentListIndex + 1
                socketio.emit('redirect_client', {'url': '/list?displaying="ingredients"'})
            elif (newInput == CVInput.INDEX and STATE.currentListIndex == len(STATE.currentRecipe.ingredients) - 1):
                STATE.currentListIndex = 0
                STATE.currentPage = AppPages.LISTINSTRUCTIONS
                socketio.emit('redirect_client', {'url': '/list?displaying="instructions"'})
            elif (newInput == CVInput.PINCH):
                resetState()
                socketio.emit('redirect_client', {'url': '/'})
        case AppPages.LISTINSTRUCTIONS:
            print('Instructions')
            if (newInput == CVInput.INDEX and STATE.currentListIndex < len(STATE.currentRecipe.instructions) - 1):
                STATE.currentListIndex = STATE.currentListIndex + 1
                socketio.emit('redirect_client', {'url': '/list?displaying="instructions"'})
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
            elif (newInput == CVInput.PINKY and STATE.currentListIndex == len(STATE.savedRecipes) - 1):
                STATE.currentPage = AppPages.LISTINGREDIENTS
                STATE.currentListIndex = 0
                socketio.emit('redirect_client', {'url': '/list?displaying="ingredients"'})
            elif (newInput == CVInput.PINCH):
                resetState()
                socketio.emit('redirect_client', {'url': '/'})
        case AppPages.INPUT:
            if (newInput == CVInput.PINCH):
                resetState()
                socketio.emit('redirect_client', {'url': '/'})

    print('tracking gestures')
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
        recipeName = request.form['name']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']

        if not recipeName or not ingredients or not instructions:
            flash('Error! Make sure all fields are filled')
            return

        if isRecipeInDatabase(recipeName, ingredients, instructions):
            flash('Recipe already in database')
            redirect('/')
            return
        
        if STATE.currentFlow == Flows.SAVE:
            saveRecipe(Recipe(recipeName, ingredients, instructions))
            redirect('/saved-confirmation')
            return
        elif STATE.currentFlow == Flows.QUICKSTART:
            STATE.currentRecipe = Recipe(recipeName, ingredients, instructions)
            redirect('/list?displaying="ingredients"')
            return

    print('rendering input template')
    return render_template('input.html')

@app.route('/list')
def listPage():
    displaying = request.args.get('displaying')

    itemsToRender = []

    if (displaying == "ingredients"):
        itemsToRender = STATE.currentRecipe.ingredients[:STATE.currentListIndex]
    elif (displaying == "instructions"):
        itemsToRender = STATE.currentRecipe.instructions[:STATE.currentListIndex]
    
    return render_template('list.html', listToRender=itemsToRender)

@app.route('/select-saved')
def selectSaved():
    return render_template('choose-saved.html', listToRender=STATE.savedRecipes, currentIndex=STATE.currentListIndex)

@app.route('/save')
def savePrompt():
    return render_template('save-prompt.html')

@app.route('/saved-confirmation')
def savedConfirmation():
    return render_template('saved-confirmation.html')



if __name__ == '__main__':
   getSavedRecipes()
   app.run()
   socketio.run(app)

   #Closing the app
   cap.release()
   cv2.destroyAllWindows()
   sched.shutdown()