#! /bin/python

"""Downloads the list of callsigns from the ISED website, parses through it, and creates an asciidoc file with a table of club callsigns within 100km of Parliament Hill in Ottawa."""

import shutil
import pandas
from zipfile import ZipFile
import csv
from urllib.request import urlretrieve
from geopy.distance import geodesic
import os
import sys
import requests
import json
import time
import logging

__author__ = "Ante Laurijssen, VA2BBW"

# Change base directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

# Set the lattitude and longitude frome where we want to calculate the distance
ottawa_lat = 45.423599
ottawa_lon = -75.701050

# Specify the url and filenames for the club callsigns files
clubs_zip_url = ("https://apc-cap.ic.gc.ca/datafiles/amateur_delim.zip")
clubs_zip_filename = "amateur_delim.zip"
clubs_txt_filename = "amateur_delim.txt"
clubs_current_csv_filename = "./csv/clubs_current.csv"
clubs_new_csv_filename = "./csv/clubs_new.csv"
clubs_local_csv_filename = "./csv/clubs_local.csv"
clubs_tmp_csv_filename = "./csv/tmp.csv"

# Target adoc filename
clubs_adoc_filename = "../club_callsigns.adoc"

# Name of person submitting this list of clubsiners
sub_name = "Ante Laurijssen, VA2BBW"

# Nominatim variables
nominatem_url_pref = "https://nominatim.openstreetmap.org/search?q="
nominatem_headers = {"User-Agent": "Ottawa-GatineauRadio411"}

# Function to calculate the distance between parliament hill and the clubsiner
def calculateDistance(club_lat, club_lon):
    distance = geodesic((club_lat, club_lon), (ottawa_lat, ottawa_lon)).kilometers
    return distance

# Function to log stdout and stderror to a log file as well as to the console

class TeeLogger:
    def __init__(self, log_file, stream):
        self.log = open(log_file, "w")
        self.stream = stream

    def write(self, message):
        self.stream.write(message)  # Print to console
        self.stream.flush()
        self.log.write(message)  # Write to log file
        self.log.flush()

    def flush(self):
        self.stream.flush()
        self.log.flush()

log_file = "logs/ised_club_calls.log"
sys.stdout = TeeLogger(log_file, sys.stdout)
sys.stderr = TeeLogger(log_file, sys.stderr)

# SCRIPT #

# Retrieve the ISED accredited clubsiner file, unzip the txt file and convert it to csv
urlretrieve(clubs_zip_url, clubs_zip_filename)
print("Downloading ISED callsign list\n")
zf = ZipFile(clubs_zip_filename)
df = pandas.read_csv(zf.open(clubs_txt_filename), delimiter = ";", dtype = str)
df_filtereded = df[df["callsign"].str.contains("VA2|VE2|VA3|VE3")]
df_filtereded.to_csv(clubs_new_csv_filename, index=False, header=False)

# Compare amateur_exmr_local and amateur_exmr, and parse only the difference between them, using the panda library, if the files exist
if os.path.isfile(clubs_local_csv_filename) and os.path.isfile(clubs_current_csv_filename):
    # Read rows from clubs_current_csv_filename
    with open(clubs_current_csv_filename) as f2:
        f2_reader = csv.reader(f2)
        f2_rows = set(tuple(row) for row in f2_reader)

    # Read rows from clubs_new_csv_filename
    with open(clubs_new_csv_filename) as f3:
        f3_reader = csv.reader(f3)
        f3_rows = set(tuple(row) for row in f3_reader)
        
    # Process clubs_local_csv_filename and filter matching rows
    with open(clubs_local_csv_filename) as f1, open(clubs_tmp_csv_filename, mode="w", newline="") as tmp_out:
        f1_reader = csv.reader(f1)
        f1_rows = set(tuple(row) for row in f1_reader)  # Create a set from the rows of f1
        f1_writer = csv.writer(tmp_out)

        for row in f1_rows:  # Iterate through f1_rows directly
            if row in f3_rows:  # If row is in f3_rows, write it to the temporary file
                f1_writer.writerow(row)

    # Move the temporary file to replace the local CSV file
    os.rename(clubs_tmp_csv_filename, clubs_local_csv_filename)
    print(f"Moved {clubs_tmp_csv_filename} to {clubs_local_csv_filename}.")

    # Process the new CSV file and compare with both f1_rows and f2_rows
    with open(clubs_new_csv_filename) as f3, open(clubs_tmp_csv_filename, mode="w", newline="") as tmp_out:
        f3_writer = csv.writer(tmp_out)

        for row in f3_rows:
            # Convert the row to a tuple and check if it's not in either f1_rows or f2_rows
            if row not in f2_rows:
                f3_writer.writerow(row)

else:
    # If files don't exist, copy the new CSV to the target paths
    shutil.copy(clubs_new_csv_filename, clubs_tmp_csv_filename)
    shutil.copy(clubs_new_csv_filename, clubs_current_csv_filename)

# Create asciidoc file
print("Writing to ../ised-accred-clubsiners.adoc\n")
with open(clubs_adoc_filename, "w") as f:
    f.write("= Club Callsigns / Indicatifs de club\n")
    f.write(":showtitle:\n\n")
    f.write("[NOTE]\n")
    f.write("====\n")
    f.write("The information presented here is based on the latest availble data from the ISED website.\n\n")
    f.write("_L'information présentée ici est basée sur les dernières données disponibles sur le site web de ISDE_\n")
    f.write("====\n\n")
    f.write(".Club Callsigns / Indicatifs de club\n")
    f.write("|===\n")
    f.write("| Callsign/Indicatif | Club | Address/Adresse | Holder/Détenteur | Submitted by/Soumis par | Reference\n\n")
        
    # Parse through the csv files and generate the asciidoc table
    count = 0
    if os.path.isfile(clubs_local_csv_filename):
        print(f"Copying still valid club callsign information from previous ISED data download from {clubs_local_csv_filename}...")
        with open(clubs_local_csv_filename, mode='r') as file:
            csvLocal = csv.reader(file)
            for lines in csvLocal:
                count += 1
                address = f"{lines[14]}, {lines[15]}, {lines[16]}, {lines[17]}"
                f.write(f"|{lines[0]}\n")
                f.write(f"|{lines[12]}\n")
                f.write(f"|{address}\n")
                f.write(f"|{lines[1]} {lines[2]}")
                f.write(f"|{sub_name}\n")
                f.write(f"|https://qrz.com/db/{lines[0]}[^]\n\n")
                print(f"\n***{lines[0]} club callsign added to the database.***\n".upper())
        print("Done copying over still valid club callsign information")
        
    with open(clubs_tmp_csv_filename, mode='r') as tmpfile:
        print("Adding new clubsiners to asciidoc file from latest ISED download...")
        csvFile = csv.reader(tmpfile)
        for lines in csvFile:
            if lines[12] != "":
                address = f"{lines[14]}, {lines[15]}, {lines[16]}, {lines[17]}"
                time.sleep(1)
                response = requests.get(f"{nominatem_url_pref}{lines[15]},{lines[16]},{lines[17]}&format=json", headers=nominatem_headers)
                try:
                    data = response.json()
                except requests.exceptions.RequestException:
                    print(f"Request Failed for {lines[0]}")
                
                if response.status_code == 200:
                    try:
                        lat = float(data[0]["lat"])
                        lon = float(data[0]["lon"])
                    except IndexError:
                        print(f"{lines[0]} not added to the database.")
                    if -90 <= lat <= 90:
                        distance = calculateDistance(lat, lon)
                        if distance <= 100:
                            with open(clubs_local_csv_filename, mode="a+") as local:
                                csvLoc = csv.writer(local)
                                count += 1
                                csvLoc.writerow(lines)
                                f.write(f"|{lines[0]}\n")
                                f.write(f"|{lines[12]}\n")
                                f.write(f"|{address}\n")
                                f.write(f"|{lines[1]} {lines[2]}")
                                f.write(f"|{sub_name}\n")
                                f.write(f"|https://qrz.com/db/{lines[0]}[^]\n\n")
                                print(f"\n***{lines[0]} added to the database.***\n".upper())
                        else:
                            print(f"{lines[0]} not added to the database.")
                    else:
                        print(f"{lines[0]} not added to the database.")
                else:
                    print(f"{lines[0]} not added to the database.")
            else:
                print(f"{lines[0]} not added to the database.")

    print(f"\n{count} club callsigns were added to the ../club_callsigns.adoc".upper())
    f.write("|===")
        
#Clean up downloaded files
print("Cleaning up downloaded files.")
os.remove(clubs_zip_filename)
print(f"Removed {clubs_zip_filename}.")
os.remove(clubs_tmp_csv_filename)
print(f"Removed {clubs_tmp_csv_filename}.")
try:
    os.rename(clubs_new_csv_filename, clubs_current_csv_filename)
except FileNotFoundError:
    os.remove(clubs_current_csv_filename)
    os.rename(clubs_new_csv_filename, clubs_current_csv_filename)
print(f"Moved {clubs_new_csv_filename} to {clubs_current_csv_filename}.")
