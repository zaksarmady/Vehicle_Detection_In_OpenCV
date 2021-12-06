# ==============================================================================
# Initialize / Import
# ==============================================================================
from video import Video
from imageprocessing import ImageProcessing, IPData
from tracking import Tracking
from car import Car
from ui import UI
from savetofile import save_to_file

# ==============================================================================
# Main
# ==============================================================================
if __name__ == '__main__':
	ui = UI()
	thisVideo = ui.init_video()	# Prompt user for video name and get video.
	tracking = Tracking()
	firstFrame = thisVideo.get_frame()
	ipData = IPData(firstFrame, 1)

	ui.settings(ipData, thisVideo, tracking)
	areas = ui.define_areas(firstFrame)
	ui.frame_width = thisVideo.videoWidth
	ui.display_width = 720
	
	limit_fps = True
	working = True
	pause = False
	
	currentCars = [] #list of cars (stored as car class)
	oldCars = [] #list of cars (stored as car class)
	
	ui.before_survey()
	
	while working:
		input_val = ui.get_input()
		
		if input_val == "quit":
			print('quitting')
			working = False		
		else:
			# Pause or resume process.
			if input_val == "pause":
				pause = not pause
			# Toggle frame limiter
			elif input_val == "regulatefps":
				limit_fps = not limit_fps
			elif input_val == "add":
				thisVideo.factors += 1
				for car in currentCars:
					car.factors += 1
			elif input_val == "subtract":
				thisVideo.factors -= 1
				for car in currentCars:
					car.factors -= 1

			if pause == False:
				frame = thisVideo.get_frame()
				if frame is None:
					print('video done')
					break
				else:
					ipData.add_frame(frame)
					ImageProcessing.main(ipData)
					oldCars += tracking.track_cars(ipData, currentCars, thisVideo.time_code(), areas)
					
					if limit_fps: thisVideo.regulate_fps()					
					ui.render_ui(ipData, currentCars, thisVideo.time_code())
	
	print("cars on screen")
	for car in currentCars:
		print(car)

	print("cars not on screen")
	for car in oldCars:
		if (car.passed_entry and car.passed_exit) and (len(car.contours) > 100) and \
				(10 < (car.last_time_seen.total_seconds() - car.first_time_seen.total_seconds()) < 60):
			print(car)
			
	# Merge lists	
	allCars = oldCars
	for car in currentCars:
		allCars.append(car)
		
	save_to_file(allCars, thisVideo)
		
	ui.exit_prompt()
	thisVideo.cleanup()
