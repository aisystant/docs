#!/usr/bin/bash

echo "Starting metadata import at $(date)"

rm -rf metadata
git clone https://github.com/aisystant/metadata.git > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Failed to clone metadata repository."
    exit 1
fi

# iterate over yaml files in the metadata directory
ls metadata/yaml | grep "sobr" | while read -r file; do
    # get name
    name=$(echo "$file" | sed 's/\.yaml//')
    echo "Importing $name"
    # remove old version if it exists
    rm -rf "docs/ru/$name"
    # import each yaml file using the import_md.py script
    #python scripts/import_md/import_md.py "$name"
    if [ $? -ne 0 ]; then
        echo "Failed to import $file"
        exit 1
    fi
    echo "Successfully imported $file"
done

rm -rf metadata
