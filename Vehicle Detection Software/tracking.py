import cv2
from imageprocessing import IPData
import datetime
from car import Car


class Tracking(object):
	def __init__(self):
		self.min_area = 2000
		self.carId = 0
		
	def track_cars(self, ipData, cars, timeCode, areas):
		contours = self.size_gate(ipData)
		contours = self.check_area_road(contours, areas['c'])
		self.add_to_car_list(cars, contours, timeCode)
		self.cull_false_positives(cars, timeCode)
		self.check_entry_exit_areas(cars, areas)
		oldCars = self.check_road_exit(cars, timeCode, areas)
		
		return oldCars
	
	# Filter out countours that are too small.
	def size_gate(self, ipData):
		contours = []
		#Loop over the contours
		for c in ipData.contours:
			#If the countour is too small, ignore it.
			if cv2.contourArea(c) < self.min_area:
				continue
				
			contours.append(c)
		return contours

	def add_to_car_list(self, cars, contours, timeCode):
		# Iterate through contours
		newCars = []
		
		if len(contours) > 0:
			for cont in contours:
			
				#simplify
				cont = cv2.convexHull(cont)
				#epsilon = 0.01*cv2.arcLength(cont,True)
				#cont = cv2.approxPolyDP(cont,epsilon,True)
				
				
				foundCar = False
				if cars != []:
					# Get coordinates of contour
					center, radius = cv2.minEnclosingCircle(cont)
					coords = [center]
					X = coords[0][0]
					Y = coords[0][1]
					
					# Iterate through cars
					for car in cars:
						current_time = int(timeCode.total_seconds())
						# Check if we can use prediction yet
						if (current_time > 0) and (len(car.coords) > 2):
							# Use prediction and intersection to match contour with existing car.
							if car.predict(X, Y, car.direction, timeCode) and self.contour_intersection(cont, car.contours[0]):  # maybe do AND interection?
								car.update_car(cont, timeCode)
								foundCar = True
						# Use intersection to match contour with existing car
						elif self.contour_intersection(cont, car.contours[0]):
							car.update_car(cont, timeCode)
							foundCar = True
				if foundCar == False:
					newCar = Car(cont, timeCode, self.carId)
					newCars.append(newCar)
					self.carId = self.carId + 1
			if len(newCars) > 0:
				for car in newCars:
					cars.append(car)
	
	# Find cars that have exited the road.
	def check_road_exit(self, cars, timeCode, areas):
		carsCPY = cars.copy()
		exitCars = []
		maxAge = datetime.timedelta(milliseconds = 180) # Around four frames
		
		# Iterate through known cars
		for car in carsCPY:
			# Check if car has passed entry and exit points.
			if self.time_since_seen(car, timeCode) < maxAge:
				continue
			
			# Last seen contour.
			rect = cv2.minAreaRect(car.contours[0])
			intersection = False
			
			# Check for partial intersection with road area
			if cv2.rotatedRectangleIntersection(rect, areas['c'])[0] == 1:
				exitCars.append(car)
				cars.remove(car)
		
		return exitCars
		
	# Ignore contours outside the area that defines the road.
	def check_area_road(self, contours, roadArea):
		inRoad = []
		# Iterate through contours.
		for c in contours:
			# create rotated rect
			rect = cv2.minAreaRect(c)
			
			# 0 is no intersection. 1 and 2 are part and total overlap.
			if cv2.rotatedRectangleIntersection(rect, roadArea)[0] != 0:
			# Eliminate the ones which do not intersect with road at all.
				inRoad.append(c)
			
		return inRoad
	
	# Check if an object is inside a specified area.
	def check_entry_exit_areas(self, cars, areas):		
		for c in cars:
			# create rotated rect
			rect = cv2.minAreaRect(c.contours[0])
			# Check for any intersection.
			# 0 is no intersection. 1 and 2 are part and total overlap.		
			if cv2.rotatedRectangleIntersection(rect, areas['a'])[0] != 0:
				c.passed_entry = True
			elif cv2.rotatedRectangleIntersection(rect, areas['b'])[0] != 0:
				c.passed_exit = True
	
	def cull_false_positives(self, cars, timeCode):
		carsCPY = cars.copy()
		for car in carsCPY:
			if car.last_time_seen != timeCode and len(car.contours) == 1:
				cars.remove(car)
				
	# Return time we have seen car move.
	def time_since_seen(self, car, currentTime):
		return currentTime - car.last_time_seen
	
	def ensure_convex(self, contour):
		if cv2.isContourConvex(contour):
			return contour
		else:
			print("was not convex")
			return cv2.convexHull(contour)
	
	def contour_intersection(self, contA, contB):		
		try:
			contAB = cv2.intersectConvexConvex(contA, contB)
		except:
			print("error in contour intersection")
			contAB = [0]
			
		if contAB[0] > 0:
			return True
		return False
