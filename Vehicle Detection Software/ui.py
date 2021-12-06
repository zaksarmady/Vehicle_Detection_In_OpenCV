import cv2
import imutils
import numpy as np
from imageprocessing import ImageProcessing, IPData
from video import Video
import copy
from car import Car
from datetime import datetime
import json


class UI(object):
	display_width = 720
	frame_width = 0

	def render_ui(self, data, cars, timestamp, debugging=False):
		frame = data.currentFrame
		text_size = self.frame_width / 768
		# Draw text and timestamp on the frame
		cv2.putText(frame, str(timestamp), (10, frame.shape[0] - 10),
					cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 0, 255), 3)

		# Draw bounding box around cars.
		for c in cars:
			# Compute the bounding box for the contour, draw it on the frame
			if debugging:
				rect = cv2.minAreaRect(c)  # Debugging gets contours
			else:
				rect = cv2.minAreaRect(c.contours[0])  # Regular gets cars.
			box = cv2.boxPoints(rect)
			box = np.int0(box)

			if not debugging:  # Draw id on frame
				id = c.id
				pos = self.right_of_box(box)
				cv2.putText(frame, str(id), (pos[0], pos[1]),
							cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 255, 0), 2)

			cv2.drawContours(frame, [box], 0, (0, 255, 0), 2)

		# Show the frame
		outframe = imutils.resize(frame, width=self.display_width)
		cv2.imshow("Tracking", outframe)

		# Enable these for debugging.
		if debugging == True:
			tempframe = data.thresh
			outframe = imutils.resize(tempframe, width=self.display_width)
			cv2.imshow("Thresh", outframe)

			tempframe = data.frameDelta
			outframe = imutils.resize(tempframe, width=self.display_width)
			cv2.imshow("Frame Delta", outframe)

	# Find rightmost point of box
	def right_of_box(self, box):
		rightmost = [0, 0]
		for i in range(0, 4):
			if box[i][0] > rightmost[0]:
				rightmost = box[i]

		return rightmost

	def before_survey(self):
		print("Survey starting")
		cv2.namedWindow('Tracking')
		cv2.setWindowProperty('Tracking', cv2.WND_PROP_TOPMOST, cv2.WINDOW_AUTOSIZE)

	def get_input(self):
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			# If the 'q' key is pressed break from the loop
			return "quit"
		elif key == ord("p"):
			return "pause"
		elif key == ord("2"):
			return "add"
		elif key == ord("1"):
			return "subtract"

	def init_video(self):
		# Find video based on user input. Raise error if not found.
		thisVideo = None
		while thisVideo == None:
			try:
				videoName = input('Please enter filename of video >> ')
				thisVideo = Video(videoName)
			except ValueError:
				thisVideo = None
				print("Could not find video: " + videoName)

		self.get_metadata(thisVideo)
		return thisVideo

	def get_metadata(self, thisVideo):
		# Check if any metadata got.
		if thisVideo.datetimeOfRecording != None:
			print("Retrieved metadata from srt file.")
			print("Datetime of recording:", thisVideo.datetimeOfRecording)
			# Display metadata, is this right
			correct = input("Is this correct? (y/n)>>").lower()

			if correct == "n":
				thisVideo.datetimeOfRecording = self.input_datetime()
		else:
			print("Could not retrieve date from srt.")
			thisVideo.datetimeOfRecording = self.input_datetime()

		# Please enter street name
		thisVideo.streetName = self.input_streetname(thisVideo.coordinatesOfRecording)
		thisVideo.factors = self.input_factors()

	def input_factors(self):
		current_factors = input("Please enter the amount of parked cars in video>>")
		current_factors = int(current_factors)
		return current_factors

	def input_datetime(self):
		gotDate = False
		while gotDate == False:
			print("please enter date in the format", end=" ")
			inputDateTime = input("YY-MM-DD HH:MM (24hour time)>>")
			# Add zeros (seconds + microseconds to match format of other datetimes.
			inputDateTime += ":00.000000"
			# check format
			try:
				datetime.strptime(inputDateTime, "%y-%m-%d %H:%M:%S.%f")
				gotDate = True
			except:
				print("The date you entered did not match the required format")

		return inputDateTime

	def input_streetname(self, coordinates):
		gotName = False
		if coordinates != None:
			print("This video was recorded at the coordinates:", coordinates)

		while gotName == False:
			streetName = input("Please enter the name of street>>")

			if streetName != None and streetName != "":
				gotName = True
			# Input does not return empty. This will not be called
			elif coordinates != None:
				# Convert coords to string, remove [ and ]
				streetName = str(coordinates)[1:-1]

		return streetName

	def settings(self, ipDataOrg, thisVideo, tracking):
		# Copy data
		ipData = copy.deepcopy(ipDataOrg)
		loopLength = 10  # Loop length in seconds.

		# Load settings
		self.JSONToSettings(thisVideo.name, ipData, tracking)

		# Create settings window
		cv2.namedWindow('settings')
		# Hard coding window size is not ideal. But could be necessary.
		cv2.resizeWindow('settings', 400, 300)

		# Create sliders
		cv2.createTrackbar('Blur', 'settings', ImageProcessing.gaussianBlurAmount[0], 60, lambda x: x)
		cv2.createTrackbar('buffer', 'settings', ipData.get_previous_frames_len(), 20, lambda x: x)
		cv2.setTrackbarMin('buffer', 'settings', 1)
		cv2.createTrackbar('Threshold', 'settings', ImageProcessing.minimumThreshold, 20, lambda x: x)
		cv2.createTrackbar('Fill', 'settings', ImageProcessing.dialateItterations, 20, lambda x: x)
		cv2.createTrackbar('min_area', 'settings', tracking.min_area, 10000,
						   lambda x: x)  # set as percentage of screen width as opposed to just a value '500'

		# Buttons not implemented in Open CV for python?
		cv2.createTrackbar('OK', 'settings', 0, 1, lambda x: x)

		# Create other windows
		cv2.namedWindow('Thresh')
		cv2.namedWindow('Frame Delta')
		cv2.namedWindow('Tracking')

		# Bring windows to front.
		cv2.setWindowProperty('Thresh', cv2.WND_PROP_TOPMOST, cv2.WINDOW_AUTOSIZE)
		cv2.setWindowProperty('Frame Delta', cv2.WND_PROP_TOPMOST, cv2.WINDOW_AUTOSIZE)
		cv2.setWindowProperty('Tracking', cv2.WND_PROP_TOPMOST, cv2.WINDOW_AUTOSIZE)
		cv2.setWindowProperty('settings', cv2.WND_PROP_TOPMOST, cv2.WINDOW_AUTOSIZE)

		print("Please adjust settings")
		# Settings loop
		changing_settings = True
		while changing_settings:
			# Get position of sliders
			gaussianBlur = cv2.getTrackbarPos('Blur', 'settings')
			ipData.set_previous_frames_len(cv2.getTrackbarPos('buffer', 'settings'))
			tracking.min_area = cv2.getTrackbarPos('min_area', 'settings')
			ImageProcessing.minimumThreshold = cv2.getTrackbarPos('Threshold', 'settings')
			ImageProcessing.dialateItterations = cv2.getTrackbarPos('Fill', 'settings')

			# Ensure Gaussian blur value is an odd number.
			if gaussianBlur % 2 == 0:
				gaussianBlur += 1
			ImageProcessing.gaussianBlurAmount = (gaussianBlur, gaussianBlur)

			# Process frame and identify cars.
			ipData.add_frame(thisVideo.get_frame())
			ImageProcessing.main(ipData)
			# cars = tracking.track_cars(ipData)
			cars = tracking.size_gate(ipData)

			self.render_ui(ipData, cars, thisVideo.time_code(), True)

			# Get key press
			k = cv2.waitKey(1) & 0xFF
			if cv2.getTrackbarPos('OK', 'settings') == 1 or k == ord("q"):
				changing_settings = False

			if thisVideo.time_code().seconds > loopLength:
				thisVideo.set_time(0)

				# Fill previous frames
				for i in range(ipData.get_previous_frames_len()):
					ipData.add_frame(thisVideo.get_frame())
					ImageProcessing.main(ipData)

		# Save settings
		self.settingsToJSON(thisVideo.name, ipData, tracking)

		# Cleanup and Exit settings
		thisVideo.set_time(0)
		ipDataOrg.set_previous_frames_len(ipData.get_previous_frames_len())
		cv2.destroyAllWindows()

	def settingsToJSON(self, name, ipData, tracking):

		# Save values in the settings dictionary
		settingsDict = {}
		settingsDict['Blur'] = ImageProcessing.gaussianBlurAmount
		settingsDict['buffer'] = ipData.get_previous_frames_len()
		settingsDict['min_area'] = tracking.min_area
		settingsDict['Threshold'] = ImageProcessing.minimumThreshold
		settingsDict['Fill'] = ImageProcessing.dialateItterations

		fileName = name + ".settings"
		jsonString = json.dumps(settingsDict)
		jsonFile = open(fileName, "w")
		jsonFile.write(jsonString)
		jsonFile.close()

	def JSONToSettings(self, name, ipData, tracking):
		try:
			fileName = name + ".settings"
			jsonFile = open(fileName, 'r')
			settingsDict = json.load(jsonFile)

			# Apply settings
			ImageProcessing.gaussianBlurAmount = settingsDict['Blur']
			ipData.set_previous_frames_len(settingsDict['buffer'])
			tracking.min_area = settingsDict['min_area']
			ImageProcessing.minimumThreshold = settingsDict['Threshold']
			ImageProcessing.dialateItterations = settingsDict['Fill']

			print("Loaded previous settings")

			return True
		except:
			# File does not exist or is incorrectly formatted
			return False

	def define_areas(self, frame):
		# Create variables
		tempArea = {'ix': -1, 'iy': -1, 'x': -1, 'y': -1, 'state': "idle"}

		# Create window
		cv2.namedWindow('set_areas')
		# Bring to front
		cv2.setWindowProperty('set_areas', cv2.WND_PROP_TOPMOST,
							  cv2.WINDOW_AUTOSIZE)
		cv2.setMouseCallback('set_areas', self.mouse_event, tempArea)

		# Dictionary that will hold the result
		result = {}
		finished = False
		while not finished:
			# Render frame
			self.frame = imutils.resize(frame, width=self.display_width)  # Resize frame
			cv2.imshow("set_areas", self.frame)
			for area in ('a', 'b', 'c'):
				print("Please draw area {}".format(area))
				tempArea['state'] = "idle"
				while tempArea['state'] != "done":
					cv2.waitKey(100)

				# store output in result dictionary
				result[area] = tempArea.copy()

			check = str(input("Are you happy with what you drew? (y/n) ")).lower().strip()

			while True:
				if check[0] == 'y':
					finished = True
					break
				elif check[0] == 'n':
					break
				else:
					check = str(input("Invalid input. Please enter y or n. ")).lower().strip()

		cv2.destroyAllWindows()
		return self.areas_to_rect(result, frame)  # Return Areas

	# Convert areas to rotatedRect
	def areas_to_rect(self, areas, frame):
		# create multiplier
		height, width, channels = frame.shape
		multiplier = int(width / self.display_width)

		for name in {'a', 'b', 'c'}:
			# Convert to corner points, multiply to return to native res.
			a = [areas[name]['x'] * multiplier, areas[name]['y'] * multiplier]
			b = [areas[name]['x'] * multiplier, areas[name]['iy'] * multiplier]
			c = [areas[name]['ix'] * multiplier, areas[name]['iy'] * multiplier]
			d = [areas[name]['ix'] * multiplier, areas[name]['y'] * multiplier]

			# minAreaRect require a Vector or Mat.
			# python can't access those constructors so numpy.narray is used.
			points = np.array([[a, b, c, d]])
			areaRect = cv2.minAreaRect(points)
			areas[name] = areaRect

		return areas

	def mouse_event(self, event, x, y, flags, tempArea):
		line_thickness = 1
		color = (0, 255, 0)
		if event == cv2.EVENT_LBUTTONDOWN and tempArea['state'] == "idle":
			tempArea['state'] = "drawing"
			self.ix, self.iy = x, y
		elif event == cv2.EVENT_MOUSEMOVE and tempArea['state'] == "drawing":
			img = imutils.resize(self.frame, width=self.display_width)  # Resize frame
			img = cv2.rectangle(img, (self.ix, self.iy), (x, y), color, line_thickness)
			cv2.imshow("set_areas", img)
		elif event == cv2.EVENT_LBUTTONUP and tempArea['state'] == "drawing":
			img = imutils.resize(self.frame, width=self.display_width)  # Resize frame
			img = cv2.rectangle(img, (self.ix, self.iy), (x, y), color, line_thickness)
			cv2.imshow("set_areas", img)
			self.frame = img
			tempArea['x'] = x
			tempArea['y'] = y
			tempArea['ix'] = self.ix
			tempArea['iy'] = self.iy
			tempArea['state'] = "done"

	def cleanup(self):
		cv2.destroyAllWindows()

	def exit_prompt(self):
		print('Press any key to exit')
		key = cv2.waitKey(0)
		self.cleanup()
