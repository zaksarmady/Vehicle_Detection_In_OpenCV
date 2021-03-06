import re
from datetime import datetime

''' Retrieves datetime, latitude and longitude from SRT file generated by your
drone. This script is written for the SRT files a DJI drone generates in 2021.
The SRT file generated by your drone might vary. If this is the case,
you should rewrite the regex patterns to find the metadata you need. '''
class SRTReader(object):
	def __init__(self, videoName):
		# Get name and add file extension
		srtName = videoName
		srtName += ".SRT"
		self.srt = None
		
		# Regex Patterns for finding metadata
		self.dtPattern = "(\d{4}-\d{2}-\d{2} [\d:,]*)"
		self.latPattern = "\[latitude : ([\d.-]*)"
		#self.longPattern = "\[longitude : ([\d.-]*)"
		self.longPattern = "\[longtitude : ([\d.-]*)"	# Spelled wrong in SRT
		
		try:
			self.srt = open(srtName, 'r')
		except:
			pass
			#print("Could not find SRT: " + srtName)
			#raise ValueError("Could not find SRT: " + videoName)
	
	# Searches SRT a datetime value.
	def get_dateTime(self):
		self.srt.seek(0, 0)	# Reset the file stream to the begining
		# Read data with regex
		foundDate = False
		while foundDate == False:
			srtLine = self.srt.readline()	
			dt = re.search(self.dtPattern, srtLine)
			if dt != None:
				foundDate = True
			elif srtLine == "":	# Check for end of file
				print("Could not find date")
				return None
		
		# Create string in a useful format
		dt = dt[1]					# Convert from re.Match to string
		dt_arr = dt.split(',')		# Remove comma from string
		dt = dt_arr[0] + '.' + dt_arr[1] + dt_arr[2] # Recombine
		# Convert to datetime
		#recordingDT = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S.%f").date()
		return dt
	
	# Searches SRT file for latitude and longitude coordinates.
	def get_coords(self):
		self.srt.seek(0, 0)	# Reset the file stream to the begining
		foundCoords = False
		while foundCoords == False:
			srtLine = self.srt.readline()
			# We assume lat and long are on the same line.
			lat = re.search(self.latPattern, srtLine)
			long = re.search(self.longPattern, srtLine)
			if (lat and long) != None:
				foundCoords = True
			elif srtLine == "":	# Check for end of file
				print("Could not find coordinates")
				return [None, None]
		
		# Convert from re.Match to float
		lat = float(lat[1])
		long = float(long[1])
		return [lat, long]
	
	def isOpened(self):
		if self.srt == None:
			return False
		return True
	