#!/bin/python

import os
from odf.opendocument import OpenDocumentSpreadsheet
from odf.table import Table, TableRow, TableCell
from odf.text import P
from bs4 import BeautifulSoup

def convert_html_to_ods(input_file, output_file):
    # Parse the HTML content using BeautifulSoup
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
    except Exception as e:
        print(f"Error parsing the HTML: {e}")
        return

    # Find the table
    table = soup.find('table')

    if not table:
        print(f"No table found in {input_file}. Skipping file.")
        return

    # Create the ODS document
    ods = OpenDocumentSpreadsheet()

    # Create the table in ODS
    odf_table = Table()

    # Process the HTML table rows and cells
    for row in table.find_all('tr'):
        ods_row = TableRow()
        for cell in row.find_all(['td', 'th']):
            ods_cell = TableCell()
            # Wrap the cell text in <text:p> element
            cell_text = cell.get_text(strip=True)
            p = P(text=cell_text)
            ods_cell.addElement(p)
            ods_row.addElement(ods_cell)
        odf_table.addElement(ods_row)

    # Add the table to the ODS document
    ods.spreadsheet.addElement(odf_table)

    # Save the ODS file
    try:
        ods.save(output_file)
        print(f"HTML table successfully converted to ODS: {output_file}")
    except Exception as e:
        print(f"Error saving ODS file: {e}")

# Define the input directory containing HTML files
input_directory = "../html"

# Define the output directory for ODS files
output_directory = "../odf"

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Loop through each .html file in the input directory
for file_name in os.listdir(input_directory):
    if file_name.endswith('.html'):
        input_file_path = os.path.join(input_directory, file_name)
        output_file_path = os.path.join(output_directory, f"{os.path.splitext(file_name)[0]}.ods")
        
        convert_html_to_ods(input_file_path, output_file_path)

print("\nConversion complete. ODS files are in the 'odf' folder.")
