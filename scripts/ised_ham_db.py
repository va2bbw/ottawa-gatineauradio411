#! /bin/python

"""Downloads the list of licensed amateur radio operators, parses through it, and creatns an asciidoc file with a table amateurs within 100km of Parliament Hill in Ottawa."""

import shutil
import pandas
from zipfile import ZipFile
import csv
from urllib.request import urlretrieve
from geopy.distance import geodesic
import os
import sys
import time
import requests
import json
import logging

__author__ = "Ante Laurijssen, VA2BBW"

# Change working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

# Set the lattitude and longitude frome where we want to calculate the distance
ottawa_lat = 45.423599
ottawa_lon = -75.701050

# Specify the url and filename for the ISED amateur database zip file
ham_zip_url = ("https://apc-cap.ic.gc.ca/datafiles/amateur_delim.zip")
ham_zip_filename = "amateur_delim.zip"
ham_txt_filename = "amateur_delim.txt"
ham_current_csv_filename = "./csv/amateur_delim_current.csv"
ham_new_csv_filename = "./csv/amateur_delim.csv"
ham_local_csv_filename = "./csv/amateur_delim_local.csv"
ham_tmp_csv_filename = "./csv/tmp.csv"
ham_processed_csv_filename = "./csv/amateur_delim_processed.csv"

# Target adoc filename
ised_ham_adoc_filename = "../ised-ham-db.adoc"

# Name of person submitting this list of licensed amateurs
sub_name = "Ante Laurijssen, VA2BBW"

# Nominatim variables
nominatem_url_pref = "https://nominatim.openstreetmap.org/search?q="
nominatem_headers = {"User-Agent": "Ottawa-GatineauRadio411"}

# Function to calculate the distance between parliament hill and the amateur
def calculateDistance(ham_lat, ham_lon):
    distance = geodesic((ham_lat, ham_lon), (ottawa_lat, ottawa_lon)).kilometers
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

log_file = "logs/ised-ham-db.log"
sys.stdout = TeeLogger(log_file, sys.stdout)
sys.stderr = TeeLogger(log_file, sys.stderr)

# SCRIPT #

# Retrieve the ISED licenced amateur file, unzip the txt file and convert it to csv
urlretrieve(ham_zip_url, ham_zip_filename)
print("Downloading ISED licenced amateur list\n")
zf = ZipFile(ham_zip_filename)
df = pandas.read_csv(zf.open(ham_txt_filename), delimiter = ";")
df_filtereded = df[df["callsign"].str.contains("VA2|VE2|VA3|VE3")]
df_filtereded.to_csv(ham_new_csv_filename, index=False, header=False)

# Compare amateur_exmr_local and amateur_exmr, and parse only the difference between them, using the panda library, if the files exist
if os.path.isfile(ham_local_csv_filename) and os.path.isfile(ham_current_csv_filename):
    # Read rows from ham_current_csv_filename
    with open(ham_current_csv_filename) as f2:
        f2_reader = csv.reader(f2)
        f2_rows = set(tuple(row) for row in f2_reader)

    # Read rows from ham_new_csv_filename
    with open(ham_new_csv_filename) as f3:
        f3_reader = csv.reader(f3)
        f3_rows = set(tuple(row) for row in f3_reader)
        
    # Process ham_local_csv_filename and filter matching rows
    with open(ham_local_csv_filename) as f1, open(ham_tmp_csv_filename, mode="w", newline="") as tmp_out:
        f1_reader = csv.reader(f1)
        f1_rows = set(tuple(row) for row in f1_reader)  # Create a set from the rows of f1
        f1_writer = csv.writer(tmp_out)

        for row in f1_rows:  # Iterate through f1_rows directly
            if row in f3_rows:  # If row is in f3_rows, write it to the temporary file
                f1_writer.writerow(row)

    # Move the temporary file to replace the local CSV file
    os.rename(ham_tmp_csv_filename, ham_local_csv_filename)
    print(f"Moved {ham_tmp_csv_filename} to {ham_local_csv_filename}.")

    # Process the new CSV file and compare with both f1_rows and f2_rows
    with open(ham_new_csv_filename) as f3, open(ham_tmp_csv_filename, mode="w", newline="") as tmp_out:
        f3_writer = csv.writer(tmp_out)

        for row in f3_rows:
            # Convert the row to a tuple and check if it's not in either f1_rows or f2_rows
            if row not in f2_rows:
                f3_writer.writerow(row)

else:
    # If files don't exist, copy the new CSV to the target paths
    shutil.copy(ham_new_csv_filename, ham_tmp_csv_filename)
    shutil.copy(ham_new_csv_filename, ham_current_csv_filename)

# Create asciidoc file
print("Writing to ../ised-ham-db.adoc\n")
with open(ised_ham_adoc_filename, "w") as f:
    f.write("= image:Logo.png[Logo,150,150] ISED Amateur Database / Base de données amateur ISDE\n")
    f.write(":showtitle:\n")
    f.write(":imagesdir: images\n")
    f.write(":data-uri:\n\n")
    f.write("[NOTE]\n")
    f.write("====\n")
    f.write("The information presented here is based on the latest availble data from the ISED website. If you are a licenced amateur in the Ottawa-Gatineau area and your information doesn't appear in this list, it is likely because you have chosen to not share your address publically in the ISED database.\n\n")
    f.write("_L'information présentée ici est basée sur les dernières données disponibles sur le site web de ISDE. Si vous êtes un radioamateur dans la région d'Ottawa-Gatineau et que votre information n'apparaît pas sure cette liste, c'est probablement parce que vous avez choisi de ne pase partager votre adresse publiquement dans la base de données de ISDE._\n")
    f.write("====\n\n")
    f.write(".ISED Amateur Database / Base de données amateur ISDE\n")
    f.write("|===\n")
    f.write("| Callsign/Indicatif | Name/Nom | Addresse | Submitted by/Soumis par | Reference\n\n")

    # Parse through the csv files and generate the asciidoc table
    count = 0
    if os.path.isfile(ham_local_csv_filename):
        print(f"Copying still valid callsign information from previous ISED data download from {ham_local_csv_filename}...")
        with open(ham_local_csv_filename, mode='r') as file, open(ham_processed_csv_filename, mode='w+') as proc:
            csvLocal = csv.reader(file)
            csvProc = csv.writer(proc)
            for lines in csvLocal:
                csvProc.writerow(lines)
                count += 1
                address = f"{lines[3]}, {lines[4]}, {lines[5]}, {lines[6]}"
                f.write(f"|{lines[0]}\n")
                f.write(f"|{lines[1]}, {lines[2]}\n")
                f.write(f"|link:++{nominatem_url_pref}{address}++[{address}^]\n")
                f.write(f"|{sub_name}\n")
                f.write(f"|https://qrz.com/db/{lines[0]}[^]\n\n")
                print(f"\n***{lines[1]} {lines[2]}, {lines[0]} added to the database.***\n".upper())                
        print("Done copying over still valid licenced amateur information")
        
    with open(ham_tmp_csv_filename, mode='r') as tmpfile, open(ham_processed_csv_filename, mode='a+') as proc:
        print("Adding new licenced amateur information to asciidoc file from latest ISED download...")
        csvFile = csv.reader(tmpfile)
        csvProc = csv.writer(proc)
        for lines in csvFile:
            address = f"{lines[3]}, {lines[4]}, {lines[5]}, {lines[6]}"
            time.sleep(1)
            response = requests.get(f"{nominatem_url_pref}{lines[4]},{lines[5]},{lines[6]}&format=json", headers=nominatem_headers)
            try:
                data = response.json()
            except requests.exceptions.RequestException:
                print(f"Request Failed for {lines[1]} {lines[2]}, {lines[0]}")
            if response.status_code == 200:
                try:
                    lat = float(data[0]["lat"])
                    lon = float(data[0]["lon"])
                except IndexError:
                    print(f"{lines[0]} not added to the database.")
                if -90 <= lat <= 90:
                    distance = calculateDistance(lat, lon)
                    if distance <= 100:
                        with open(ham_local_csv_filename, mode="a+") as local:
                            csvLoc = csv.writer(local)
                            count += 1
                            csvLoc.writerow(lines)
                            f.write(f"|{lines[0]}\n")
                            f.write(f"|{lines[1]} {lines[2]}\n")
                            f.write(f"|link:++{nominatem_url_pref}{address}++[{address}^]\n")
                            f.write(f"|{sub_name}\n")
                            f.write(f"|https://qrz.com/db/{lines[0]}[^]\n\n")
                            print(f"\n***{lines[0]} added to the database.***\n".upper())
                    else:
                            print(f"{lines[0]} not added to the database.")
                else:
                    print(f"{lines[0]} not added to the database.")
            else:
                print(f"{lines[0]} not added to the database")
            csvProc.writerow(lines)
    print(f"\n{count} licenced amateurs were added to the ../ised-ham-db.adoc".upper())
    f.write("|===")

#Clean up downloaded files
print("Cleaning up downloaded files.")
os.remove(ham_zip_filename)
print(f"Removed {ham_zip_filename}.")
os.remove(ham_tmp_csv_filename)
print(f"Removed {ham_tmp_csv_filename}.")
try:
    os.rename(ham_new_csv_filename, ham_current_csv_filename)
except FileNotFoundError:
    os.remove(ham_current_csv_filename)
    os.rename(ham_new_csv_filename, ham_current_csv_filename)
print(f"Moved {ham_new_csv_filename} to {ham_current_csv_filename}.")
