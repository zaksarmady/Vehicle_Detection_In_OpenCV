import cv2
import imutils
from collections import deque

# A class for holding and transporting image processing data.
class IPData(object):
	def __init__(self, frame, numOfFrames):
		self.frameDelta = None
		self.thresh = None
		self.grey = ImageProcessing.image_processing(frame)
		self.currentFrame = None
		self.contours = None
		# deque is a list which can have a limited length.
		self.__previousFrame = deque([], maxlen=numOfFrames)
	
	# Saves current frame. Adds old currentFrame to previousFrame
	def add_frame(self, frame):
		# Oldest frame is deleted if there are more than numOfFrames.
		self.__previousFrame.append(self.grey)
		self.currentFrame = frame
	
	# Returns oldest previous frame
	def get_previous_frame(self):
		return self.__previousFrame[0]
	
	def get_previous_frames_len(self):
		return self.__previousFrame.maxlen
	
	def set_previous_frames_len(self, newLength):
		newPrevousFrame = deque([], maxlen=newLength)
		for frame in self.__previousFrame:
			newPrevousFrame.append(frame)
		self.__previousFrame = newPrevousFrame

class ImageProcessing(object):
	gaussianBlurAmount = (21, 21)
	minimumThreshold = 5
	dialateItterations = 10
	
	@staticmethod
	def main(data):	#previously process_frame()
		data.grey = ImageProcessing.image_processing(data.currentFrame)
		data.contours = ImageProcessing.find_motion(data)
		
		return data.contours
	
	@staticmethod
	def image_processing(frame):
		#Resize the frame, convert it to grayscale, and blur it
		grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		grey = cv2.GaussianBlur(grey, ImageProcessing.gaussianBlurAmount, 0)

		return grey
	
	@staticmethod
	def find_motion(data):
		#Compute the absolute difference between the current frame and the first frame
		frameDelta = cv2.absdiff(data.get_previous_frame(), data.grey)
		thresh = cv2.threshold(frameDelta, ImageProcessing.minimumThreshold,
													255, cv2.THRESH_BINARY)[1]

		#Dialate the thresholded image to fill in holes, then find contours on thresholded image
		thresh = cv2.dilate(thresh, None,
							iterations = ImageProcessing.dialateItterations)

		data.frameDelta = frameDelta
		data.thresh = thresh
		
		contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
									cv2.CHAIN_APPROX_SIMPLE)
		contours = imutils.grab_contours(contours)
		
		return contours