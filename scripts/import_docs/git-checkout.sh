#!/bin/bash

name=$1
version=$2

git fetch --all
#git checkout main
git pull



branch="$name/$version"
git checkout -b "$branch"
