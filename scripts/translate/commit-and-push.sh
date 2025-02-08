#!/bin/bash

course=$1
version=$2
language=$3

GIT_AUTHOR_NAME="GitHub Action" \
GIT_AUTHOR_EMAIL="github-actions[bot]@users.noreply.github.com" \
GIT_COMMITTER_NAME="GitHub Action" \
GIT_COMMITTER_EMAIL="github-actions[bot]@users.noreply.github.com" \

BRANCH="en/$course/$version"
MSG="Translate $course ($version) to $language"

git checkout $BRANCH
git add docs/$language/$course
git commit -m "$MSG"

#git checkout main
git push --set-upstream origin $BRANCH

gh pr create --title "Translate $course to $language" --body "$MSG" --base main --head $BRANCH
