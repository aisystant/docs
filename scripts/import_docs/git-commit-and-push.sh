#!/bin/bash

name=$1
version=$2
authors=$3
changelog=$4

# save old git username and email
old_username=$(git config user.name)
old_email=$(git config user.email)

# set git username and email
author_info=$(python scripts/import_docs/get_author_info.py "$authors")
author_name=$(echo $author_info | cut -d: -f1)
author_email=$(echo $author_info | cut -d: -f2)
git config user.name "$author_name"
git config user.email "$author_email"

git add docs/ru/$name
msg=$(echo $changelog | base64 -d)
git commit -m "$msg"
git push origin $name/$version

git config user.name "$old_username"
git config user.email "$old_email"

# Create gh pull request
gh pr create --title "$msg" --body "$msg" --base main --head "$name/$version"