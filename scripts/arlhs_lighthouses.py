#! /bin/python

import re
import csv
from urllib.request import urlretrieve
from geopy.distance import geodesic
from geopy.point import Point
import os
import sys
from bs4 import BeautifulSoup
import pandas
from io import StringIO

# Change working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

# Set the lattitude and longitude frome where we want to calculate the distance
ottawa_lat = 45.423599
ottawa_lon = -75.701050

# Specify the url and filename for the downloaded data from arlhs database
arlhs_htmldb_url = ("https://wlol.arlhs.com/index.php?mode=zones&zone=CAN")
arlhs_htmldb_filename = "lighthouses_list.html"
arlhs_csv_filename = "lighthouses_list.csv"

# Target adoc filename
arlhs_adoc_filename = "../arlhs-lighthouses.adoc"

# SOTA website prefix - for use with reference links + lighthouse ref#
arlhs_site_pref = "https://wlol.arlhs.com/lighthouse/"

# GoogleMaps url prefix
google_maps_url_pref = "https://maps.google.com/maps?t=k&q="

# Name of person submitting these parks
sub_name = "Ante Laurijssen, VA2BBW"

# Function to calculate the distance between parliament hill and the park
def calculateDistance(lh_lat, lh_lon):
    distance = geodesic((lh_lat, lh_lon), (ottawa_lat, ottawa_lon)).kilometers
    return distance

# Retrieve the ARLHS htmldb file for Canada
print(f"Downloading {arlhs_htmldb_url} ... ... ...")
urlretrieve(arlhs_htmldb_url, arlhs_htmldb_filename)

# Extract table from the hmtl file with Panda
with open(arlhs_htmldb_filename) as file:
    soup = BeautifulSoup(file, 'html.parser')
tables = pandas.read_html(StringIO(str(soup)))
df = tables[0]
df.to_csv(arlhs_csv_filename, index=False)

# Function to clean up the unwanted symbols in the lat/lon degrees from the table

def dmm_to_dd(coord):
    """Convert Degrees and Decimal Minutes (DMM) to Decimal Degrees (DD)."""
    match = re.match(r"(\d+)°\s*([\d.]+)'\s*([NSEW])", coord)
    if not match:
        raise ValueError(f"Invalid coordinate format: {coord}")

    degrees, minutes, direction = match.groups()
    dd = float(degrees) + float(minutes) / 60

    # Make it negative for South or West
    if direction in ['S', 'W']:
        dd *= -1

    return dd

with open(arlhs_adoc_filename, "w") as f:
    f.write("= ARLHS Lighthouses / Phares ARLHS\n")
    f.write(":showtitle:\n\n")
    f.write(".ARLHS Lighthouses / Phares ARLHS\n")
    f.write("|===\n")
    f.write("| ARLHS Number/Numéro ARLHS | Name/Nom | Location | Submitted by/Soumis par | Reference\n\n")

    with open(arlhs_csv_filename, mode='r') as file:
        csvFile = csv.reader(file)
        for lines in csvFile:
            if len(lines) >1 and lines[1].startswith("CAN"):  # Simplified check
                try:
                    if lines[4] != "-" and lines[5] != "-":
                        lat = round(dmm_to_dd(lines[4]), 4)
                        lon = round(dmm_to_dd(lines[5]), 4)
                    if -90 <= lat <= 90:
                        distance = calculateDistance(lat, lon)
                        if distance <= 100:
                            f.write(f"|{lines[1]}\n")
                            f.write(f"|{lines[0]}\n")
                            f.write(f"|{google_maps_url_pref}{lat},{lon}[{lat},{lon}^]\n")
                            f.write(f"|{sub_name}\n")
                            f.write(f"|{arlhs_site_pref}{lines[1].replace(" ", "")}.html[^]\n\n")
                            print(f"\n***Lighthouse {lines[1]} added to the database.***\n".upper())
                        else:
                            print(f"Lighthouse {lines[1]} not added to the database.")
                    else:
                        print(f"Lighthouse {lines[1]} not added to the database.")
                except ValueError:
                     print(f"Lighthouse {lines[1]} not added to the database.")
    f.write("|===")

# Clean up files
print("Cleaning up downloaded files")
os.remove(arlhs_csv_filename)
os.remove(arlhs_htmldb_filename)
