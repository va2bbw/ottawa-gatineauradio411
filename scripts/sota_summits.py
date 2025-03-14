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

# Specify the url and filename for the SOTA summits csv file
sota_csv_url = ("https://storage.sota.org.uk/summitslist.csv")
sota_csv_filename = "summitslist.csv"

# Target adoc filename
sota_adoc_filename = "../sota-summits.adoc"

# SOTA website prefix - for use with reference links + summit ref#
sota_site_pref = "https://www.sotadata.org.uk/en/summit/"

# Name of person submitting these parks
sub_name = "Ante Laurijssen, VA2BBW"

# Function to calculate the distance between parliament hill and the park
def calculateDistance(summit_lat, summit_lon):
    distance = geodesic((summit_lat, summit_lon), (ottawa_lat, ottawa_lon)).kilometers
    return distance

# Retrieve the SOTA summits csv file
urlretrieve(sota_csv_url, sota_csv_filename)

with open(sota_adoc_filename, "w") as f:
    f.write("= SOTA Summits / Sommets SOTA\n")
    f.write(":showtitle:\n\n")
    f.write(".SOTA Summits / Sommets SOTA\n")
    f.write("|===\n")
    f.write("| Summit/Sommet | Name/Nom | Location | Submitted by/Soumis par | Reference\n\n")

    with open(sota_csv_filename, mode='r') as file:
        csvFile = csv.reader(file)
        for lines in csvFile:
            if len(lines) >1 and lines[1].startswith("Canada"):  # Simplified check
                 try:
                    lat, lon = float(lines[9]), float(lines[8])  # Convert to float once
                    if -90 <= lat <= 90:
                        distance = calculateDistance(lat, lon)
                        if distance <= 100:
                            f.write(f"|{lines[0]}\n|{lines[3]}\n|{lat}, {lon}\n|{sub_name}\n|{sota_site_pref}{lines[0]}[^]\n\n")
                 except ValueError:
                     print(f"Skipping invalid lat/lon: {lines[9]}, {lines[8]}")
    f.write("|===")
