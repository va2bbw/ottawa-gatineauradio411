#! /bin/python

"""Downloads the list of accredited examiners from the ISED website, parses through it, and creates an asciidoc file with a table of examiners within 100km of Parliament Hill in Ottawa."""

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

# Specify the url and filenames for the ISED accredited examiners files
exam_zip_url = ("https://apc-cap.ic.gc.ca/datafiles/amateur_exmr.zip")
exam_zip_filename = "amateur_exmr.zip"
exam_txt_filename = "amateur_exmr.txt"
exam_current_csv_filename = "./csv/amateur_current_exmr.csv"
exam_new_csv_filename = "./csv/amateur_exmr.csv"
exam_local_csv_filename = "./csv/amateur_exmr_local.csv"
exam_tmp_csv_filename = "./csv/tmp.csv"

# Target adoc filename
accred_exam_adoc_filename = "../ised-accred-examiners.adoc"

# Name of person submitting this list of examiners
sub_name = "Ante Laurijssen, VA2BBW"

# Nominatim variables
nominatem_url_pref = "https://nominatim.openstreetmap.org/search?q="
nominatem_headers = {"User-Agent": "Ottawa-GatineauRadio411"}

# Function to calculate the distance between parliament hill and the park
def calculateDistance(exmr_lat, exmr_lon):
    distance = geodesic((exmr_lat, exmr_lon), (ottawa_lat, ottawa_lon)).kilometers
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

log_file = "logs/ised-accredited-examiners.log"
sys.stdout = TeeLogger(log_file, sys.stdout)
sys.stderr = TeeLogger(log_file, sys.stderr)

# SCRIPT #

# Retrieve the ISED accredited examiner file, unzip the txt file and convert it to csv
urlretrieve(exam_zip_url, exam_zip_filename)
print("Downloading ISED accredited examiners list\n")
zf = ZipFile(exam_zip_filename)
df = pandas.read_csv(zf.open(exam_txt_filename), delimiter = ";", dtype = str)
df.to_csv(exam_new_csv_filename, index=False, header = False)

# Compare amateur_exmr_local and amateur_exmr, and parse only the difference between them, using the panda library, if the files exist
if os.path.isfile(exam_local_csv_filename) and os.path.isfile(exam_current_csv_filename):
    # Read rows from exam_current_csv_filename
    with open(exam_current_csv_filename) as f2:
        f2_reader = csv.reader(f2)
        f2_rows = set(tuple(row) for row in f2_reader)

    # Read rows from exam_new_csv_filename
    with open(exam_new_csv_filename) as f3:
        f3_reader = csv.reader(f3)
        f3_rows = set(tuple(row) for row in f3_reader)
        
    # Process exam_local_csv_filename and filter matching rows
    with open(exam_local_csv_filename) as f1, open(exam_tmp_csv_filename, mode="w", newline="") as tmp_out:
        f1_reader = csv.reader(f1)
        f1_rows = set(tuple(row) for row in f1_reader)  # Create a set from the rows of f1
        f1_writer = csv.writer(tmp_out)

        for row in f1_rows:  # Iterate through f1_rows directly
            if row in f3_rows:  # If row is in f3_rows, write it to the temporary file
                f1_writer.writerow(row)

    # Move the temporary file to replace the local CSV file
    os.rename(exam_tmp_csv_filename, exam_local_csv_filename)
    print(f"Moved {exam_tmp_csv_filename} to {exam_local_csv_filename}.")

    # Process the new CSV file and compare with both f1_rows and f2_rows
    with open(exam_new_csv_filename) as f3, open(exam_tmp_csv_filename, mode="w", newline="") as tmp_out:
        f3_reader = csv.reader(f3)
        f3_writer = csv.writer(tmp_out)

        for row in f3_rows:
            # Convert the row to a tuple and check if it's not in either f1_rows or f2_rows
            if tuple(row) not in f1_rows and tuple(row) not in f2_rows:
                f3_writer.writerow(row)

else:
    # If files don't exist, copy the new CSV to the target paths
    shutil.copy(exam_new_csv_filename, exam_tmp_csv_filename)
    shutil.copy(exam_new_csv_filename, exam_current_csv_filename)

    # Create asciidoc file
print("Writing to ../ised-accred-examiners.adoc\n")
with open(accred_exam_adoc_filename, "w") as f:
    f.write("= ISED Accredited Examiners / Examinateurs accrédités ISDE\n")
    f.write(":showtitle:\n\n")
    f.write("[NOTE]\n")
    f.write("====\n")
    f.write("The information presented here is based on the latest availble data from the ISED website.\n")
    f.write("_L'information présentée ici est basée sur les dernières données disponibles sur le site web de ISDE_\n")
    f.write("====\n\n")
    f.write(".ISED Accredited Examiners / Examinateurs accrédités ISDE\n")
    f.write("|===\n")
    f.write("| Name/Nom | Addresse | Telephone | email/courriel | Submitted by/Soumis par | Reference\n\n")
        
    # Parse through the csv files and generate the asciidoc table
    count = 0
    if os.path.isfile(exam_local_csv_filename):
        print(f"Copying still valid examiner information from previous ISED data download from {exam_local_csv_filename}...")
        with open(exam_local_csv_filename, mode='r') as file:
            csvLocal = csv.reader(file)
            for lines in csvLocal:
                count +=1
                address = f"{lines[2]}, {lines[3]}, {lines[4]}, {lines[9]}"
                f.write(f"|{lines[0]} {lines[1]}\n")
                f.write(f"|{address}\n")
                f.write(f"|link:tel:{lines[5][:-2]}[({lines[5][:3]}) {lines[5][3:6]}-{lines[5][6:10]}]")
                if lines[6] != "":
                    f.write(f", link:tel:{lines[6][:-2]}[({lines[6][:3]}) {lines[6][3:6]}-{lines[6][6:10]}]\n")
                f.write(f"|{lines[7]}\n")
                f.write(f"|{sub_name}\n")
                f.write(f"|https://apc-cap.ic.gc.ca/pls/apc_anon/query_examiner_amat$.startup[ISED^]\n\n")
                print(f"\n***{lines[0]} {lines[1]} added to the database.***\n".upper())
        print("Done copying over still valid examiner information")
        
    with open(exam_tmp_csv_filename, mode='r') as tmpfile:
        print("Adding new examiners to asciidoc file from latest ISED download...")
        csvFile = csv.reader(tmpfile)
        for lines in csvFile:
            if lines[4].startswith(("ON", "QC")):
                address = f"{lines[2]}, {lines[3]}, {lines[4]}, {lines[9]}"
                time.sleep(1)
                response = requests.get(f"{nominatem_url_pref}{lines[3]}, {lines[4]}, {lines[9]}&format=json", headers=nominatem_headers)
                try:
                    data = response.json()
                except requests.exceptions.JSONDecodeError:
                    print("Failed to decode JSON. Possible API block or error page.")
                if response.status_code == 200:
                    try:
                        lat = float(data[0]["lat"])
                        lon = float(data[0]["lon"])
                    except IndexError:
                        print(f"{lines[0]} {lines[1]} not added to the database.")
                    if -90 <= lat <= 90:
                        distance = calculateDistance(lat, lon)
                        if distance <= 100:
                            with open(exam_local_csv_filename, mode="a+") as local:
                                csvLoc = csv.writer(local)
                                count +=1
                                csvLoc.writerow(lines)
                                f.write(f"|{lines[0]} {lines[1]}\n")
                                f.write(f"|{address}\n")
                                f.write(f"|link:tel:{lines[5]}[({lines[5][:3]}) {lines[5][3:6]}-{lines[5][6:]}]")
                                if lines[6] != "":
                                    f.write(f", link:tel:{lines[6]}[({lines[6][:3]}) {lines[6][3:6]}-{lines[6][6:]}]\n")
                                f.write(f"|{lines[7]}\n")
                                f.write(f"|{sub_name}\n")
                                f.write(f"|https://apc-cap.ic.gc.ca/pls/apc_anon/query_examiner_amat$.startup[ISED^]\n\n")
                                print(f"\n***{lines[0]} {lines[1]} added to the database.***\n".upper())
                        else:
                            print(f"{lines[0]} {lines[1]} not added to the database.")
                    else:
                        print(f"{lines[0]} {lines[1]} not added to the database.")
                else:
                    print(f"{lines[0]} {lines[1]} not added to the database.")
            else:
                print(f"{lines[0]} {lines[1]} not added to the database.")

    print(f"\n{count} examiners were added to the ../ised-accred-examiners.adoc".upper())
    f.write("|===")
        
#Clean up downloaded files
print("Cleaning up downloaded files.")
os.remove(exam_zip_filename)
print(f"Removed {exam_zip_filename}.")
os.remove(exam_tmp_csv_filename)
print(f"Removed {exam_tmp_csv_filename}.")
try:
    os.rename(exam_new_csv_filename, exam_current_csv_filename)
except FileNotFoundError:
    os.remove(exam_current_csv_filename)
    os.rename(exam_new_csv_filename, exam_current_csv_filename)
print(f"Moved {exam_new_csv_filename} to {exam_current_csv_filename}.")
