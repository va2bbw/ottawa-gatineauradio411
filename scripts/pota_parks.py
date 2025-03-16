#! /bin/python

import csv
from urllib.request import urlretrieve
from geopy.distance import geodesic
import os
import sys

# Change working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

# Set the lattitude and longitude frome where we want to calculate the distance
ottawa_lat = 45.423599
ottawa_lon = -75.701050

# Specify the url and filename for the POTA parks csv file
pota_csv_url = ("https://pota.app/all_parks_ext.csv")
pota_csv_filename = "all_parks_ext.csv"

# Target adoc filename
pota_adoc_filename = "../pota-parks.adoc"

# Pota website prefix - for use with reference links + park ref#
pota_site_pref = "https://pota.app/#/park/"

# Name of person submitting these parks
sub_name = "Ante Laurijssen, VA2BBW"

# Function to calculate the distance between parliament hill and the park
def calculateDistance(park_lat, park_lon):
    distance = geodesic((park_lat, park_lon), (ottawa_lat, ottawa_lon)).kilometers
    return distance

# Retrieve the POTA parks csv file
urlretrieve(pota_csv_url, pota_csv_filename)

with open(pota_adoc_filename, "w") as f:
    f.write("= POTA Parks / Parcs POTA\n")
    f.write(":showtitle:\n\n")
    f.write(".POTA Parks / Parcs POTA\n")
    f.write("|===\n")
    f.write("| Park/Parc | Name/Nom | Location | Submitted by/Soumis par | Reference\n\n")

    with open(pota_csv_filename, mode='r') as file:
        csvFile = csv.reader(file)
        for lines in csvFile:
            if lines[0].startswith("CA"):  # Simplified check
                try:
                    lat, lon = float(lines[5]), float(lines[6])  # Convert to float once
                    if -90 <= lat <= 90:
                        distance = calculateDistance(lat, lon)
                        if distance <= 100:
                            f.write(f"|{lines[0]}\n|{lines[1]}\n|{lat}, {lon}\n|{sub_name}\n|{pota_site_pref}{lines[0]}[^]\n\n")
                            print(f"\n***Park {lines[0]} added to the database.***\n".upper())
                        else:
                            print(f"Park {lines[0]} not added to the database.")
                except ValueError:
                    print(f"Park {lines[0]} not added to the database.")
    f.write("|===")
