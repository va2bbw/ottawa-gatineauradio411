#! /bin/python

import pandas
from zipfile import ZipFile
import csv
from urllib.request import urlretrieve
from geopy.distance import geodesic
import os
import sys
from time import sleep
import requests

# Change working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

# Set the lattitude and longitude frome where we want to calculate the distance
ottawa_lat = 45.423599
ottawa_lon = -75.701050

# Specify the url and filename for the ISED accredited examiners zip file
exam_zip_url = ("https://apc-cap.ic.gc.ca/datafiles/amateur_exmr.zip")
exam_zip_filename = "amateur_exmr.zip"
exam_txt_filename = "amateur_exmr.txt"
exam_csv_filename = "amateur_exmr.csv"

# Target adoc filename
accred_exam_adoc_filename = "../ised-accred-examiners.adoc"

# Name of person submitting these parks
sub_name = "Ante Laurijssen, VA2BBW"

# Google geocode api key
google_geocode_api_key = open(".google_geocode_api_key.txt", "r").read()

# Function to calculate the distance between parliament hill and the park
def calculateDistance(exmr_lat, exmr_lon):
    distance = geodesic((exmr_lat, exmr_lon), (ottawa_lat, ottawa_lon)).kilometers
    return distance

# Retrieve the ISED accredited examiner file, unzip the txt file and convert it to csv
urlretrieve(exam_zip_url, exam_zip_filename)
zf = ZipFile(exam_zip_filename)
df = pandas.read_csv(zf.open(exam_txt_filename), delimiter = ";")
df.to_csv(exam_csv_filename, index=False)

with open(accred_exam_adoc_filename, "w") as f:
    f.write("= ISED Accredited Examiners / Examinateurs accrédités ISDE\n")
    f.write(":showtitle:\n\n")
    f.write(".ISED Accredited Examiners / Examinateurs accrédités ISDE\n")
    f.write("|===\n")
    f.write("| Name/Nom | Addresse | Telephone | email/courriel | Submitted by/Soumis par | Reference\n\n")

    with open(exam_csv_filename, mode='r') as file:
        csvFile = csv.reader(file)
        for lines in csvFile:
            address = f"{lines[2]}, {lines[3]}, {lines[4]}, {lines[9]}"
            api_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'.format(address, google_geocode_api_key))
            api_response_dict = api_response.json()
            if api_response_dict['status'] == 'OK':
                try:
                    lat = api_response_dict['results'][0]['geometry']['location']['lat']
                    lon = api_response_dict['results'][0]['geometry']['location']['lng']
                    if -90 <= lat <= 90:
                        distance = calculateDistance(lat, lon)
                        if distance <= 100:
                            f.write(f"|{lines[0]} {lines[1]}\n|{lines[2]}, {lines[3]}, {lines[4]}, {lines[9]}\n|({lines[5][:3]}) {lines[5][3:6]}-{lines[5][6:10]}, ({lines[6][:3]}) {lines[6][3:6]}-{lines[6][6:10]}\n|{lines[7]}\n|{sub_name}\n|https://apc-cap.ic.gc.ca/pls/apc_anon/query_examiner_amat$.startup[ISED^]\n\n")
                            print(f"\n***{lines[0]} {lines[1]} added to the database.***\n".upper())
                        else:
                            print(f"{lines[0]} {lines[1]} not added to the database.")
                except ValueError:
                    print(f"{lines[0]} {lines[1]} not added to the database.")
        f.write("|===")
