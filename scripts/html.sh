#!/bin/sh

# Get the directory of the script and change to it
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check if there is an 'html' folder; if not, create one
mkdir -p ../html

# Loop through each .adoc file in the current directory
for file in ../*.adoc; do
  # Check if the file exists
  if [ -f "$file" ]; then
    # Check if the file is readme.adoc and convert it to index.html
    if [ "$file" = "../readme.adoc" ]; then
      # Convert readme.adoc to index.html
      asciidoctor -s "$file" -o "../html/index.html"
    else
      # For all other .adoc files, convert them to their base name with .html
      base_name=$(basename "$file" .adoc)
      asciidoctor -s "$file" -o "../html/$base_name.html"
    fi
  fi
done

echo "Conversion complete. HTML files are in the 'html' folder."
