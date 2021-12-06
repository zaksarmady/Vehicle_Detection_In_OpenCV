import cv2


class Car(object):
	def __init__(self, contour, first_time_seen, car_id, passed_entry = False):
		self.id = car_id
		self.contours = [contour]
		self.first_time_seen = first_time_seen
		self.last_time_seen = first_time_seen
		self.coords = [self.find_center(contour)]
		self.passed_entry = passed_entry
		self.passed_exit = False
		self.speedX = None
		self.speedY = None
		self.predict_posX = None
		self.predict_posY = None
		self.direction = ""
		self.factors = 0
		
	
	def find_center(self, contour):
		center = None
		radius = None
		center, radius = cv2.minEnclosingCircle(contour)

		return center
		
	def update_car(self, contour, timeCode):		
		# Position 0 contains the most recent contour and coords.
		self.contours.insert(0, contour)
		self.coords.insert(0, self.find_center(contour))
		
		self.last_time_seen = timeCode

	def not_moving(self, X, Y, timeCode):
		last_time_seen = int(self.last_time_seen.total_seconds())
		current_time = int(timeCode.total_seconds())
		if last_time_seen > (current_time + 5):
			if X == self.coords[0][0]:
				return False

	def check_direction(self, direction):
		if direction == self.direction:
			if direction != "":
				if self.direction != "":
					return True
		else:
			return False

	def predict(self, X, Y, direction, timeCode):
		coorX = int(0 if X is None else X)
		coorY = int(0 if Y is None else Y)

		self.speedX = self.coords[0][0] - self.coords[1][0]
		self.speedY = self.coords[0][1] - self.coords[1][1]
		self.predict_posX = self.coords[0][0] + self.speedX
		self.predict_posY = self.coords[0][1] + self.speedY
		if self.speedX > 0:
			self.direction = "left"
		if self.speedX < 0:
			self.direction = "right"
		else:
			self.direction = ""

		int_predict_posX = int(0 if self.predict_posX is None else self.predict_posX)
		int_predict_posY = int(0 if self.predict_posY is None else self.predict_posY)

		last_time_seen = int(self.last_time_seen.total_seconds())
		current_time = int(timeCode.total_seconds())

		if X is None:
			return False
		elif Y is None:
			return False
		elif self.not_moving(X, Y, timeCode) is False:
			return False
		elif last_time_seen > (current_time + 2): #change this to 2 seconds. or even 1.
			return False
		# elif self.check_direction(direction) is True:
		elif int_predict_posX - 40 <= coorX <= int_predict_posX + 40:  # put the direction and standing in one place here in this loop
			if int_predict_posY - 40 <= coorY <= int_predict_posY + 40:
				return True
		else:
			return False
	
	def __str__(self):
		# First seen last seen, times observed
		return "ID: {0} First seen:{1} Last seen:{2} Hit both checkpoints:{3} Times observed:{4} Time Taken{5}".format(
			self.id,
			self.first_time_seen,
			self.last_time_seen,
			(self.passed_entry and self.passed_exit),
			len(self.contours),
			self.last_time_seen - self.first_time_seen)
