#!/bin/bash

name=$1
version=$2
versionId=$3
#authors=$3
#changelog=$4

# For each course, run the import script
#echo "Importing course: $name, version: $version, authors: $authors, changelog: $changelog"
#python scripts/import_docs/import_course.py "$name" "$version"
echo "Importing course: $name, version: $version, versionId: $versionId"
mkdir -p tmp/$name/$version
python scripts/import_docs/01_get_course_structure.py "$versionId" > tmp/$name/$version/structure.json
cat tmp/$name/$version/structure.json | python scripts/import_docs/02_get_sections.py > tmp/$name/$version/sections.json
cat tmp/$name/$version/sections.json | python scripts/import_docs/03_make_slug.py > tmp/$name/$version/slug.json
cat tmp/$name/$version/slug.json | python scripts/import_docs/write_structure.py docs/$name
