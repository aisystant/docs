#!/usr/bin/bash

echo "Starting metadata import at $(date)"

rm -rf metadata
git clone https://github.com/aisystant/metadata.git > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Failed to clone metadata repository."
    exit 1
fi

# iterate over yaml files in the metadata directory
ls metadata/yaml | while read -r file; do
    # get name
    name=$(echo "$file" | sed 's/\.yaml//')
    echo "Importing $name"
    # remove old version if it exists (check both old flat structure and new category structure)
    rm -rf "docs/ru/$name"
    rm -rf "docs/ru/personal/$name"
    rm -rf "docs/ru/professional/$name" 
    rm -rf "docs/ru/uncategorized/$name"
    rm -rf "docs/public/ru/$name"
    rm -rf "docs/public/ru/personal/$name"
    rm -rf "docs/public/ru/professional/$name"
    rm -rf "docs/public/ru/uncategorized/$name"
    # import each yaml file using the import_md.py script
    python scripts/import_md/import_md.py "$name" "$1"
    if [ $? -ne 0 ]; then
        echo "Failed to import $file"
        exit 1
    fi
    echo "Successfully imported $file"
done

rm -rf metadata
