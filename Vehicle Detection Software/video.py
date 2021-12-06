from imutils.video import VideoStream
from srt_reader import SRTReader
import datetime
import time
import cv2

class Video(object):
	def __init__(self, videoName):
		# Open video file
		self.vs = cv2.VideoCapture(videoName)
		
		# Metadata
		self.datetimeOfRecording = None
		self.coordinatesOfRecording = None
		self.streetName = None
		self.factors = None

		self.nextFrameTime = time.time()
		
		if self.vs.isOpened():
			# Get other metadata
			# Save videoname
			self.name = videoName.split('.')[0] # Remove file extension
			# Get frames per second
			self.frameRate = self.vs.get(cv2.CAP_PROP_FPS)
			self.videoWidth = self.vs.get(cv2.CAP_PROP_FRAME_WIDTH)
			# Find miliseconds per frame
			self.msecondsPerFrame = 1000 / self.frameRate
			
			#Open SRT
			reader = SRTReader(self.name)
			
			# Get Metadata from SRT
			if reader.isOpened():
				self.datetimeOfRecording = reader.get_dateTime()
				self.coordinatesOfRecording = reader.get_coords()
				
			self.frameNum = 0
		else:
			raise ValueError("Could not find video: " + videoName)
		
	def get_frame(self):
		# Grab the current frame
		frame = self.vs.read()[1]   #frame[0] is a bool, returns false if no frame.

		# Enable this if processing is slow
		# frame = imutils.resize(frame, width=500)
		
		self.frameNum += 1
		return frame
	
	def set_time(self, timeStamp):
		# Set current time to timeStamp which is milliseconds.
		self.vs.set(cv2.CAP_PROP_POS_MSEC, timeStamp)
		
	def time_code(self):
		# Get playback position in mseconds
		timeStamp = self.vs.get(cv2.CAP_PROP_POS_MSEC)
		
		# framenum x frametime
		#timeStamp = self.frameNum * self.msecondsPerFrame	#milliseconds
		
		# Convert to timedelta
		timeStamp = datetime.timedelta(milliseconds = timeStamp)
		
		return timeStamp
	
	def cleanup(self):
		self.vs.release()

	def regulate_fps(self):
		# Wait until it's time to play frame
		timeNow = time.time()
		if self.nextFrameTime > timeNow:
			aTime = self.nextFrameTime - timeNow
			time.sleep(aTime)
			self.nextFrameTime += self.msecondsPerFrame/1000
		else:
			self.nextFrameTime = timeNow + self.msecondsPerFrame/1000
			
		