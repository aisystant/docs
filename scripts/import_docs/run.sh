# Get a list of cources from the api (run get_all_cources.sh, that return a list of cources)

# python scripts/import_docs/get_all_cources.py | while read -r course; do
python scripts/import_docs/get_all_cources.py | grep systems-thinking-introduction | while read -r course; do
    # course=name:version:authors:changelog
    echo "Course: $course"
    name=$(echo $course | cut -d: -f1)
    version=$(echo $course | cut -d: -f2)
    versionId=$(echo $course | cut -d: -f3)
    authors=$(echo $course | cut -d: -f4)
    changelog=$(echo $course | cut -d: -f5-)
    bash scripts/import_docs/git-update.sh "$name" "$version"
    if [ $? -ne 0 ]; then
        echo "Error checking out branch"
        exit 1
    fi
    bash scripts/import_docs/process_course.sh "$name" "$version" "$versionId"
    echo "Run manually:"
    echo bash scripts/import_docs/git-commit-and-push.sh "$name" "$version" "$authors" "$changelog"  # remove echo after debug
    break
done
