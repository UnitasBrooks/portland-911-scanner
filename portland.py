import feedparser
import googlemaps
from datetime import datetime
from geopy.distance import great_circle
import time
import argparse

URL = "http://www.portlandonline.com/scripts/911incidents.cfm"
TIME_PATTERN = "%Y-%m-%dT%H:%M:%S.%f"


def get_elapsed_time(time_string):
    """
    Get's the elapsed seconds since the incident
    :param time_string: time string from incident
    :return: now - time of incident in seconds
    """
    epoch = datetime(1970, 1, 1)
    epoch_time_of_entry = int((datetime.strptime(time_string, TIME_PATTERN) - epoch).total_seconds()) + (7 * 3600)
    return int(time.time()) - int(epoch_time_of_entry)


def scan(seconds, miles, api_key=None, address=None, lat_lng=None):
    """
    Prints out all incidents in the last N seconds, within a X mile radius
    :param seconds: number of seconds
    :param miles: number of miles
    :param api_key: Google maps API key to get the coordinates of your location
    :param address: Address to search around
    :param lat_lng: Latitude and longitude to search around
    :return: A list of matching incident strings
    """
    if lat_lng is None:
        gmaps = googlemaps.Client(key=api_key)
        geocode_result = gmaps.geocode(address)
        lat_lng = geocode_result[0]["geometry"]["location"]

        my_lat = lat_lng["lat"]
        my_long = lat_lng["lng"]
        lat_lng = (my_lat, my_long)

    entries = feedparser.parse(URL)["entries"]
    matching_incidents = []
    for entry in entries:
        incident_location = entry["where"]["coordinates"]
        fixed_location = (incident_location[1], incident_location[0])
        distance = great_circle(fixed_location, lat_lng).miles

        if distance < miles:
            time_string = "-".join(entry["published"].split("-")[:-1])
            if get_elapsed_time(time_string) < seconds:
                return_string = ""
                return_string += entry["summary"] + "\n\n"
                return_string += time_string + "\n\n"
                return_string += "https://www.google.com/maps/place/" + \
                                 str(fixed_location[0]) + "," + str(fixed_location[1]) + "\n\n"
                return_string += "Distance: " + str(distance) + " miles" + "\n\n"
                return_string += "\n\n"

                print return_string
                matching_incidents.append(return_string)

    return matching_incidents


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Portland 911 Scanner.')
    parser.add_argument("--miles", default=1.0, type=float, help="Number of miles to check")
    parser.add_argument("--hours", default=1, type=int, help="How many hours back to check")
    parser.add_argument("--address", type=str, help="Address to search around")
    parser.add_argument("--api_key", type=str, help="Google maps API key")
    args = parser.parse_args()

    scan(seconds=args.hours * 60 * 60, miles=args.miles, api_key=args.api_key, address=args.address)
