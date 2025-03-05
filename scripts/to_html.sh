#!/bin/sh
# Script to convert all the adoc files to html

echo "Converting files to html..."

# Create the html folder

echo "creating 'html' folder"

mkdir -p ../html

# Loop through each .adoc file in the current directory
for file in ../*.adoc; do
  # Check if the file exists
  if [ -f "$file" ]; then
      # Convert adoc files to their base name with .html
      base_name=$(basename "$file" .adoc)
      asciidoctor -s "$file" -o "../html/$base_name.html"
      echo "Converted $file to $base_name.html"
  fi
done

echo
echo "Conversion to HTML complete. HTML files are in the 'html' folder."
echo
