#! /bin/python

import csv # needed to work with csv files
from urllib.request import urlretrieve # needed for retrieving files with url
from geopy.distance import geodesic # needed to calculate distance between two lat/lon points
import os
import sys

# Change working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

# Set the lattitude and longitude frome where we want to calculate the distance
# Parliament Hill
ottawa_lat = 45.423599
ottawa_lon = -75.701050

# Specify the url and filename for the SOTA summits csv file
sota_csv_url = ("https://storage.sota.org.uk/summitslist.csv")
sota_csv_filename = "summitslist.csv"

# Target adoc filename
sota_adoc_filename = "../sota-summits.adoc"

# SOTA website prefix - for use with reference links + summit ref#
sota_site_pref = "https://www.sotadata.org.uk/en/summit/"

# OpenTopoMap url prefix
otm_maps_url_pref = "https://opentopomap.org/"

# Name of person submitting these parks
sub_name = "Ante Laurijssen, VA2BBW"

# Function to calculate the distance between parliament hill and the park
def calculateDistance(summit_lat, summit_lon):
    distance = geodesic((summit_lat, summit_lon), (ottawa_lat, ottawa_lon)).kilometers
    return distance

# Retrieve the SOTA summits csv file
urlretrieve(sota_csv_url, sota_csv_filename)
print("Downloading SOTA csv file")

# Adoc file creation with title and table
with open(sota_adoc_filename, "w") as f:
    f.write("= SOTA Summits / Sommets SOTA\n")
    f.write(":showtitle:\n\n")
    f.write(".SOTA Summits / Sommets SOTA\n")
    f.write("|===\n")
    f.write("| Summit/Sommet | Name/Nom | Location | Height (m)/Hauteur (m) | Submitted by/Soumis par | Reference\n\n")

    # Function to parse through the csv file, choose the ones only from Canada, then only those within 100km of Parliament Hill and add to the table
    with open(sota_csv_filename, mode='r') as file:
        csvFile = csv.reader(file)
        count = 0
        for lines in csvFile:
            if len(lines) >1 and lines[1].startswith("Canada"):  # Simplified check
                 try:
                    lat, lon = float(lines[9]), float(lines[8])  # Convert to float once
                    if -90 <= lat <= 90:
                        distance = calculateDistance(lat, lon)
                        if distance <= 100:
                            count +=1
                            f.write(f"|{lines[0]}\n")
                            f.write(f"|{lines[3]}\n")
                            f.write(f"|{otm_maps_url_pref}#marker=15/{lat}/{lon}[{lat}, {lon}^]\n")
                            f.write(f"|{lines[4]}\n")
                            f.write(f"|{sub_name}\n")
                            f.write(f"|{sota_site_pref}{lines[0]}[^]\n\n")
                            print(f"\n***Summit {lines[0]} added to the database.***\n".upper())
                        else:
                            print(f"Summit {lines[0]} not added to the database.")
                    else:
                        print(f"Summit {lines[0]} not added to the database.")
                 except ValueError:
                     print(f"Summit {lines[0]} not added to the database.")
    f.write("|===")
    print(f"{count} summits added to the list.")
    
# Clean up files
print("Cleaning up downloaded files")
os.remove(sota_csv_filename)
