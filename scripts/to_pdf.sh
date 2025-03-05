#!/bin/sh
# Script to convert all the adoc files to pdf

echo "Converting files to pdf..."

# Create the pdf folder

echo "creating 'pdf' folder"

mkdir -p ../pdf

# Loop through each .adoc file in the current directory
for file in ../*.adoc; do
  # Check if the file exists
  if [ -f "$file" ]; then
      # Convert adoc files to their base name with .pdf
      base_name=$(basename "$file" .adoc)
      asciidoctor -r asciidoctor-pdf -b pdf -o "../pdf/$base_name.pdf" "$file"
      echo "Converted $file to $base_name.pdf"
  fi
done

echo
echo "Conversion to PDF complete. PDF files are in the 'pdf' folder."
echo
