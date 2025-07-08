import time
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

class CVInput(Enum):
	INDEX = 1
	MIDDLE = 2
	PINKY = 3
	PINCH = 4
     
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
	            
				if (IsPinchGesture() and CVInput.PINCH in validOptions):
					timeOfLastInput = time.time()
					return CVInput.PINCH
				elif (IsIndexTouchingThumb() and CVInput.INDEX in validOptions):
					timeOfLastInput = time.time()
					return CVInput.INDEX
				elif (IsMiddleTouchingThumb() and CVInput.MIDDLE in validOptions):
					timeOfLastInput = time.time()
					return CVInput.MIDDLE
				elif (IsPinkyTouchingThumb() and CVInput.PINKY in validOptions):
					timeOfLastInput = time.time()
					return CVInput.PINKY