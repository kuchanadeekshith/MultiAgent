import requests
import csv
import pandas as pd
import math
from math import radians, sin, cos, sqrt, asin


user_lat=18.93352
user_long=72.823485


import requests
from math import radians, sin, cos, sqrt, asin

# Haversine formula to compute distance between two coordinates
def haversine_manual(lat1, lon1, lat2, lon2):
    R = 6371  # km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# Convert address to coordinates
# location.py



'''

def add_to_cord(address="mumbai+jail"):
#Assuming theres access to any free api which return text to lat and long
    API="68e64855a7b07586524369dsi111827" 

    url=f"https://geocode.maps.co/search?q={address}&api_key={API}"
    response=requests.get(url)
    response=response.json()
    user_lat=response[0]['lat']
    user_long=response[0]['lon']
    return user_lat,user_long


distance_manual = haversine_manual(float(store_lat),float( store_long), user_lat, user_long)
print(f"Manual distance calculation: {distance_manual:.2f} km")'''