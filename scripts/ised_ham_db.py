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

# Specify the url and filename for the ISED amateur database zip file
ham_zip_url = ("https://apc-cap.ic.gc.ca/datafiles/amateur_delim.zip")
ham_zip_filename = "amateur_delim.zip"
ham_txt_filename = "amateur_delim.txt"
ham_csv_filename = "amateur_delim_qc-on.csv"

# Target adoc filename
ised_ham_adoc_filename = "../ised-ham-db.adoc"

# Name of person submitting these parks
sub_name = "Ante Laurijssen, VA2BBW"

# Google geocode api key
google_geocode_api_key = open(".google_geocode_api_key.txt", "r").read()

# Function to calculate the distance between parliament hill and the park
def calculateDistance(ham_lat, ham_lon):
    distance = geodesic((ham_lat, ham_lon), (ottawa_lat, ottawa_lon)).kilometers
    return distance

# Retrieve the ISED accredited examiner file, unzip the txt file and convert it to csv
urlretrieve(ham_zip_url, ham_zip_filename)
zf = ZipFile(ham_zip_filename)
#df = pandas.read_csv(zf.open(ham_txt_filename), delimiter = ";")
df = pandas.read_csv(zf.open(ham_txt_filename), delimiter = ";")
df_filtered = df[df["callsign"].str.contains("VA2|VE2|VA3|VE3")]
df_filtered.to_csv(ham_csv_filename, index=False)

with open(ised_ham_adoc_filename, "w") as f:
    f.write("= ISED Amateur Database / Base de données amateur ISDE\n")
    f.write(":showtitle:\n\n")
    f.write(".ISED Amateur Database / Base de données amateur ISDE\n")
    f.write("|===\n")
    f.write("| Callsign/Indicatif | Name/Nom | Addresse | Submitted by/Soumis par | Reference\n\n")

    with open(ham_csv_filename, mode='r') as file:
        csvFile = csv.reader(file)
        for lines in csvFile:
            address = f"{lines[4]}, {lines[5]}, {lines[6]}, {lines[7]}"
            api_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'.format(address, google_geocode_api_key))
            api_response_dict = api_response.json()
            if api_response_dict['status'] == 'OK':
                try:
                    lat = api_response_dict['results'][0]['geometry']['location']['lat']
                    lon = api_response_dict['results'][0]['geometry']['location']['lng']
                    if -90 <= lat <= 90:
                        distance = calculateDistance(lat, lon)
                        if distance <= 100:
                            f.write(f"|{lines[0]}\n|{lines[1]} {lines[2]}\n|{lines[3]}, {lines[4]}, {lines[5]}, {lines[6]}\n|{sub_name}\n|https://qrz.com/db/{lines[0]}[^]\n\n")
                            print(f"\n***{lines[0]} added to the database.***\n".upper())
                        else:
                            print(f"{lines[0]} not added to the database.")
                except ValueError:
                    print(f"{lines[0]} not added to the database.")
            else:
                print(f"{lines[0]} not added to the database")
        f.write("|===")
