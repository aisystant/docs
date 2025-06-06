#!/usr/bin/bash

echo "Starting translation with metadata at $(date)"

rm -rf metadata
git clone https://github.com/aisystant/metadata.git > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Failed to clone metadata repository."
    exit 1
fi

# iterate over yaml files in the metadata directory
ls metadata/yaml | grep "systems-think" | while read -r file; do
    # get name
    name=$(echo "$file" | sed 's/\.yaml//')
    echo "Translating $name"
    mv "docs/en/$name" "docs/en/bak.$name"
    # rm -rf "docs/public/en/$name"
    # import each yaml file using the import_md.py script
    python scripts/translate_md/translate_md.py "$name" $1
    if [ $? -ne 0 ]; then
        echo "Failed to import $file"
        exit 1
    fi
    echo "Successfully translated $file"
    echo "Removing old version of $name"
    rm -rf "docs/en/bak.$name"
done

rm -rf metadata
