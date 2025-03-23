#!/bin/sh

# Get the directory of the script and change to it
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting conversion of files..."
echo

./to_html_embed.sh &&
    
./to_html.sh &&

./to_docs.sh &&

./to_pdf.sh &&

exit
