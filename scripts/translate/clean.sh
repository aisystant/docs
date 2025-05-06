#!/bin/bash 

# Remove all .md files in $1 directory and its subdirectories
# Usage: ./clean.sh <directory>

# Check if the directory is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Check if the directory exists
if [ ! -d "$1" ]; then
    echo "Error: Directory $1 does not exist."
    exit 1
fi

# Find and remove all .md files in the specified directory
find "$1" -type f -name "*.md" -exec rm -f {} \;
echo "Removed all .md files in $1 directory and its subdirectories."
