#!/bin/sh
# Script to convert all the adoc files to html

echo "Converting files to embedded HTML..."

# Create the html folder

echo "creating 'html_embed' folder"

mkdir -p ../html_embed

# Loop through each .adoc file in the current directory
for file in ../*.adoc; do
  # Check if the file exists
  if [ -f "$file" ]; then
      # Convert adoc files to their base name with .html
      base_name=$(basename "$file" .adoc)
      asciidoctor -b html5 -s "$file" -o "../html_embed/$base_name.html"
      echo "Converted $file to $base_name.html"
  fi
done

echo
echo "Conversion to embedded HTML complete. Files are in the 'html_embed' folder."
echo
