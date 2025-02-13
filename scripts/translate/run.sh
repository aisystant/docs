#!/bin/bash

git fetch --all
git pull

# First of all we need to get the commits for comparison from arguments
commit1=$1
commit2=$2

# Then we need to get the files that were changed between the two commits
#files=$(git diff --name-only $commit1 $commit2)

# lets translate all the files in docs/ru directory
files=$(find docs/ru -type f)

## Let's check if all the files are in docs/ru directory
#for file in $files
#do
#
#done

# Now let's translate all the files
for file in $files
do
    if [[ $file != docs/ru/* ]]
    then
        echo "Error: $file is not in docs/ru directory"
        continue
    fi
    python scripts/translate/translate.py $file
done