#!/bin/sh
# Script to convert all the adoc files to html

echo "Copying html files to docs for github.io page..."

# Create the html folder

echo "creating 'docs' folder"

mkdir -p ../docs

# Loop through each .adoc file in the current directory
for file in ../html/*.html; do
  # Check if the file exists
  if [ -f "$file" ]; then
      cp "$file" ../docs/
      echo "Copied $file to docs"
  fi
done

mv ../docs/readme.html ../docs/index.html
echo "Moved docs/readme.html to docs/index.html"

echo
echo "Copying to docs complete. Files are in the 'docs' folder."
echo
