import json
from video import Video


def cars_to_dict(cars):
    # Return a list of cars stored as dicts
    dictCars = []
    for car in cars:
        # Timedelta converted to string ([H]H:MM:SS.ffffff)
        carDict = {
            "id": car.id,
            "first_time_seen": str(car.first_time_seen),
            "last_time_seen": str(car.last_time_seen),
            "passed_entry_exit": car.passed_entry and car.passed_exit,
            "factors_affected": car.factors
        }
        dictCars.append(carDict)

    return dictCars


def write_file(dictCars, video):
    videoDict = {
        "Video Name": video.name,
        "Street Name": video.streetName,
        "Date/Time Recorded": video.datetimeOfRecording,
        "Coordinates": video.coordinatesOfRecording,
        "Number of Factors": video.factors,
        "cars": dictCars
    }
    videoJson = json.dumps(videoDict, indent=4)

    # Opens file or creates a new one if it doesn't exist.
    with open(video.name + ".json", "w") as outfile:
        outfile.write(videoJson)


def save_to_file(cars, videoName):
    # convert to dict
    dictCars = cars_to_dict(cars)
    # write to file
    write_file(dictCars, videoName)
