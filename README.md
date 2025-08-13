# Sous - Computer Vision Powered Recipe Reader for Mac

Sous is a recipe reader that you can use with dirty hands!
I built this as I have been getting into cooking recently and hate having to stop what I am doing to wash my hands so that I can scroll to the next part of the recipe.

## Technical Information

Sous is a Flask-based application that uses OpenCV and MediaPipe to track the user's hand gestures for input. It is a Flask server with a finite state machine that uses gestures to move between states and serve HTML to the browser.
A web-socket handles redirection and refreshes

## How to install

1. Clone the repo `git clone https://github.com/seanpourgoutzidis/Sous.git`
2. Create virtual environment `python -m venv venv`
3. Source the virtual environment `source venv/bin/activate`
4. Run `pip install -r requirements.txt` to install requirements
5. Setup app `export FLASK_APP=app`
6. Run `flask run`

> [!NOTE]
> For a snazzier running setup, I recommend creating a `Shortcut` in the `Shortcuts` app to run a Terminal Script that changes directory to Sous and `flask run` the application.
> If you don't want to use the UI version. I've attached a CLI version of Sous to this repo called `sous-cli`.

## User Manual

* Touch index and thumb - primary input. Select the 1st option or move down a list.
* Touch middle and thumb - secondary input. Select the 2nd option of move up a list.
* Touch pinky and thumb - tertiary input. Select the 3rd option or confirm selection
* Pinch index, middle and thumb - Move back to homepage. If already on homepage, shutdown the app.

## Demo

[Link to Demo](https://youtu.be/KjYgKfUZ7S4)
