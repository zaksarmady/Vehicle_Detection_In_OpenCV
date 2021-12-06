import unittest
from video import Video
from imageprocessing import ImageProcessing, IPData
from tracking import Tracking
import datetime
import time
#==============================================================================
# Tests
#==============================================================================

class TestVideoMethods(unittest.TestCase):
	def test_open_video(self):
		thisVideo = None
		thisVideo = Video("DJI_613_Black-480.mp4")
		
		# Function has completed. Function has returned something.
		self.assertIsNotNone(thisVideo)
		return thisVideo
		
	def test_get_frame(self):
		thisVideo = Video("DJI_613_Black-480.mp4")
		frame = None
		frame = thisVideo.get_frame()
		
		# Function has completed. Function has returned something.
		self.assertIsNotNone(frame)
	
	def test_time_code(self):
		frameRate = 29.97
		thisVideo = Video("DJI_613_Black-480.mp4")		
		for x in range(0, 121):
			thisVideo.get_frame()
		timeCode = thisVideo.time_code()
		
		# Mili-seconds per frame is (1000/29.97) = 33.3667
		# 121 * 33.3667 =~ 4 seconds
		self.assertEqual(timeCode.seconds, 4)
	
	def test_set_time_code(self):
		timeMS = 30 * 1000
		thisVideo = Video("DJI_613_Black-480.mp4")
		
		thisVideo.set_time(timeMS)
		thisVideo.get_frame()
		thisVideo.get_frame()
		timeCode = thisVideo.time_code()
		self.assertEqual(timeCode.seconds, 30)
	'''
	def test_regulate_fps(self):
		timeMS = 30 * 1000
		thisVideo = Video("DJI_613_Black-480.mp4")
		delta = []
		
		thisVideo.regulate_fps()
		for i in range(120):
			before = time.time()
			thisVideo.regulate_fps()
			after = time.time()
			delta.append( (after - before) * 1000)
		
		avgDelta = sum(delta)/len(delta)
		
		print("\n Delta", avgDelta, "ms per frame", thisVideo.msecondsPerFrame)
		self.assertTrue(avgDelta > thisVideo.msecondsPerFrame)
		'''
	
	def test_regulate_fps2(self):
		timeMS = 30 * 1000
		thisVideo = Video("DJI_613_Black-480.mp4")
		thisVideo.nextFrameTime = -1
		testLength = 240
		times = []
		
		thisVideo.regulate_fps()
		for i in range(testLength):
			thisVideo.regulate_fps()
			thisVideo.get_frame()
			times.append(time.time())
		
		timedeltas = []
		for i in range( 1, testLength):
			delta = (times[i] - times[i-1]) * 1000
			timedeltas.append(delta)
			
		avgDelta = sum(timedeltas)/len(timedeltas)
		fps = 1000/avgDelta
		print("\n Frames per seconds", fps, "Expected fps", thisVideo.frameRate)
		self.assertTrue(avgDelta > thisVideo.msecondsPerFrame)


class TestImageProcessingMethods(unittest.TestCase):
	def setUp(self):
		self.thisVideo = Video("DJI_613_Black-480.mp4")
		
		# Init data class
		frame = self.thisVideo.get_frame()
		self.ipData = IPData(frame, 3)
		
		# data class now has a currentFrame and previousFrame.
		frame = self.thisVideo.get_frame()
		self.ipData.add_frame(frame)
		
	def test_image_processing(self):
		grey = ImageProcessing.image_processing(self.ipData.currentFrame)
		# Function has completed. It has returned something.
		self.assertIsNotNone(grey)
	
	def test_find_motion(self):
		self.ipData.grey = ImageProcessing.image_processing(self.ipData.currentFrame)
		contours = ImageProcessing.find_motion(self.ipData)
		# Function has identified more than 0 moving objects.
		self.assertTrue(len(contours) > 0)
	
	def test_main(self):
		# self.ipData is as it was in setUp.
		self.assertIsNone(self.ipData.thresh)
		
		tempContours = ImageProcessing.main(self.ipData)
		
		# ImageProcessing has returned more than 0 moving objects.
		self.assertTrue(len(tempContours) > 0)
		
		# The changes to self.ipData have persisted without being returned.
		self.assertTrue(len(self.ipData.contours) > 0)
		self.assertIsNotNone(self.ipData.thresh)
		

class TestIPDataMethods(unittest.TestCase):
	def setUp(self):
		self.thisVideo = Video("DJI_613_Black-480.mp4")
		frame = self.thisVideo.get_frame()
		
		self.processingData = IPData(frame, 3)
		self.frame = self.thisVideo.get_frame()
	
	def test_init(self):
		# Init has returned an instance of IPData()
		# The instance variables are None.
		self.assertIsNone(self.processingData.frameDelta)
		self.assertIsNone(self.processingData.thresh)
		self.assertIsNotNone(self.processingData.grey)
	
	def test_add_frame(self):
		self.processingData.add_frame(self.frame)
		self.assertIsNotNone(self.processingData.currentFrame)
		self.assertIsNotNone(self.processingData.get_previous_frame())
	
	def test_arr_size(self):		
		frame = self.thisVideo.get_frame()
		

class TestTrackingMethods(unittest.TestCase):
	def setUp(self):
		self.thisVideo = Video("DJI_613_Black-480.mp4")
		
		# Init data class
		frame = self.thisVideo.get_frame()
		self.ipData = IPData(frame, 3)
		
		# data class now has a currentFrame and previousFrame.
		frame = self.thisVideo.get_frame()
		self.ipData.add_frame(frame)
		
		ImageProcessing.main(self.ipData)
	
	def test_track_cars(self):
		tracking = Tracking()
		
		cars = tracking.track_cars(self.ipData.contours)
		
		# Function has identified more than 0 moving objects.
		self.assertTrue(len(cars) > 0)
		
	
	
#==============================================================================
# Test Utilities
#==============================================================================



if __name__ == '__main__':
	unittest.main(verbosity=2)
