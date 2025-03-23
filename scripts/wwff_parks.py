#! /bin/python

import csv
import requests
from urllib.request import urlretrieve
from geopy.distance import geodesic
import os
import sys

# Change working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

# Set the lattitude and longitude frome where we want to calculate the distance
# Parliament Hill
ottawa_lat = 45.423599
ottawa_lon = -75.701050

# Specify the url and filename for the WWFF parks csv file
wwff_csv_url = ("https://wwff.co/wwff-data/wwff_directory.csv")
wwff_csv_filename = "wwff_directory.csv"

# Target adoc filename
wwff_adoc_filename = "../wwff-parks.adoc"

# Wwff website prefix - for use with reference links + park ref#
wwff_site_pref = "https://wwff.co/directory/"

# OpenStreetMap url prefix
osm_maps_url_pref = "https://openstreetmap.org/"

# Name of person submitting these parks
sub_name = "Ante Laurijssen, VA2BBW"

# Function to calculate the distance between parliament hill and the park
def calculateDistance(park_lat, park_lon):
    distance = geodesic((park_lat, park_lon), (ottawa_lat, ottawa_lon)).kilometers
    return distance

# Retrieve the WWFF parks csv file
print(f"Downloading {wwff_csv_url} ... ... ...")
r = requests.get(wwff_csv_url)
open(wwff_csv_filename, "wb").write(r.content)

with open(wwff_adoc_filename, "w") as f:
    f.write("= WWFF Parks / Parcs WWFF\n")
    f.write(":showtitle:\n\n")
    f.write(".WWFF Parks / Parcs WWFF\n")
    f.write("|===\n")
    f.write("| Park/Parc | Name/Nom | Location | Submitted by/Soumis par | Reference\n\n")
    with open(wwff_csv_filename, mode='r') as file:
        count = 0
        csvFile = csv.reader(file)
        for lines in csvFile:
            if lines[0].startswith("VEFF"):  # Simplified check
                try:
                    lat, lon = float(lines[10]), float(lines[11])  # Convert to float once
                    if -90 <= lat <= 90:
                        distance = calculateDistance(lat, lon)
                        if distance <= 100:
                            count +=1
                            f.write(f"|{lines[0]}\n")
                            f.write(f"|{lines[2]}\n")
                            f.write(f"|{osm_maps_url_pref}?mlat={lat}&mlon={lon}&zoom=19[{lat}, {lon}^]\n")
                            f.write(f"|{wwff_site_pref}[^]\n\n")
                            print(f"\n***Park {lines[0]} added to the database.***\n".upper())
                        else:
                            print(f"Park {lines[0]} not added to the database.")
                except ValueError:
                    print(f"Park {lines[0]} not added to the database.")
            else:
                print(f"Park {lines[0]} not added to the database.")
    f.write("|===")
    print(f"{count} parks added to the list.")
# Clean up files
print("Cleaning up downloaded files")
os.remove(wwff_csv_filename)
