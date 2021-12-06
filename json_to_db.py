from datetime import datetime, timedelta
import mysql.connector
import json

def connect_to_database():
	try:
		mydb = mysql.connector.connect(
		  host="localhost",
		  user="user",
		  password="password",
		  database="trafficproj"
		)
	except:
		print("Could not connect to database.")
		print("Check user details and confirm db instance is running.")
		

	mycursor = mydb.cursor()
	return mydb, mycursor

# Return id of street, or none if street doesn't exist.
def street_id(mycursor, name):
	sql = "SELECT * FROM STREETS WHERE name = %s"
	#sql = "SELECT * FROM streets"
	val = (name, )
	result = None
	
	try:
		#mycursor.execute(sql, val)
		mycursor.execute(sql, val)
		result = mycursor.fetchone()
	except mysql.connector.errors.InterfaceError:
		print("Street does not exist in database")
	
	if result != None:
		return result[0]
	return None

def insert_street(name, mycursor, mydb):
	sql = "INSERT INTO STREETS (name, suburb, length, width) VALUES (%s, %s, %s, %s)"
	length = None
	width = None
	getting_input = True
	
	while getting_input == True:
		# Ask user for subburb of street.
		suburb = input('Please enter name of suburb >>')
		# Ask user if they know length and width of street/area surveyed.
		
		dimensions = input('Do you know length and width of street/area surveyed (y/n)>>')
		if dimensions == 'y':
			length = input('Please enter length of street/area surveyed >>')
			width = input('Please enter length of street/area surveyed >>')
		
		print("Street is {0}, Suburb: {1}, Length: {2}, Width: {3}".format(
			name,
			suburb,
			length,
			width))
		
		confirm = get_yes_no('Is this correct (y/n) >>')
		if confirm == "y": getting_input = False
		
	#val = ('Atkinson St', 'Chadstone', None, None)
	val = (name, suburb, length, width)
	mycursor.execute(sql, val)
	
	# Return new street id.
	return mycursor.lastrowid

# If JSON data is already in table, maybe we don't want to continue.
def data_already_inserted(mycursor, streetID, recorded):
	recordedNoMS = recorded.split('.')[0]
	sql = "SELECT * FROM EVENTS WHERE streetID = %s AND recorded = %s"
	val = (streetID, recordedNoMS, )
	result = None
	
	try:
		mycursor.execute(sql, val)
		result = mycursor.fetchall()
	except mysql.connector.errors.InterfaceError:
		pass
		
	
	if result != []:
		print("This json file has already been uploaded to the database.")
		question = "Would you like to overwrite existing records? (y/n)>>"
		overwrite = get_yes_no(question)
		
		if overwrite == 'y':
			sql = "delete FROM EVENTS WHERE streetID = %s AND recorded = %s"
			val = (streetID, recordedNoMS)
			mycursor.execute(sql, val)
			print(mycursor.rowcount, "record(s) deleted")
		# Json already written to db, user doesn't want to proceed.
		elif overwrite == 'n':
			return True
		
	return False

def insert_event_into_database(mycursor, eventDict, streetID):
	sql = "INSERT INTO EVENTS"
	sql += "(recorded, timeCaptured, entered, exited, full, numFactors, streetID)"
	sql += "VALUES (%s, %s, %s, %s, %s, %s, %s)"
	recorded = eventDict['Date/Time Recorded']
	numFactors = None
	
	convert_car_times(eventDict['cars'])
	
	
	values = []
	# Iterate through records
	for event in eventDict['cars']:
		
		#timeTaken = lastSeen - firstSeen
		timeTaken = event['last_time_seen'] - event['first_time_seen']
		otherCars = other_cars_on_road(event, eventDict['cars'])
		factors = event['factors_affected'] + otherCars
		
		
		# Eliminate some false positives
		if timeTaken.total_seconds() > 0:
			val = (recorded,
					timeTaken,
					event['first_time_seen'],
					event['last_time_seen'],
					event['passed_entry_exit'],
					factors,
					streetID)
			values.append(val)
	
	# Execute insert statement
	mycursor.executemany(sql, values)

# Find number of cars on road concurrent with this one
def other_cars_on_road(car, carDict):	
	firstSeen = car['first_time_seen']
	lastSeen = car['last_time_seen']
	numCars = 0
	
	for otherCar in carDict:
		if car == otherCar:
			continue
		
		if firstSeen > otherCar['last_time_seen'] or lastSeen < otherCar['first_time_seen']:
			pass
		else:
			numCars += 1
	
	return numCars

def convert_car_times(carDict):
	for car in carDict:
		# Convert timestamps to timedelta
		dt = datetime.strptime(car['first_time_seen'], '%H:%M:%S.%f')
		firstSeen = timedelta(hours = dt.hour, minutes = dt.minute,
						seconds = dt.second, microseconds = dt.microsecond)
		dt = datetime.strptime(car['last_time_seen'], '%H:%M:%S.%f')
		lastSeen = timedelta(hours = dt.hour, minutes = dt.minute,
						seconds = dt.second, microseconds = dt.microsecond)
		
		# Add to dictionary
		car['first_time_seen'] = firstSeen
		car['last_time_seen'] = lastSeen
	

def open_json(name):
	fileName = name
	jsonFile = open(fileName, 'r')
	eventDict = json.load(jsonFile)
	return eventDict

def get_yes_no(question):
	gotInput = False
	while gotInput == False:
		answer = input(question).lower()
		if answer == 'y' or answer == 'n':
			gotInput = True
	return answer

if __name__ == '__main__':
	eventDict = None
	# open json
	while eventDict == None:
		jsonName = input('Please enter filename of json file >>')
		try:
			eventDict = open_json(jsonName)
		except ValueError:
			eventDict = None
			print("Could not find json file: " + videoName)
	strName = eventDict["Street Name"]
	
	# connect to db
	mydb, mycursor = connect_to_database()
	
	# Check if street already exists in db.
	str_id = street_id(mycursor, strName)
	
	alreadyInserted = False
	if str_id == None:
		# Insert new street
		str_id = insert_street(strName, mycursor, mydb)
	else:
		alreadyInserted = data_already_inserted(mycursor,
									str_id, eventDict["Date/Time Recorded"])
	
	if alreadyInserted:
		print("No records changed, quitting")
	else:
		insert_event_into_database(mycursor, eventDict, str_id)
		mydb.commit()
		print("Data succesfully inserted.")