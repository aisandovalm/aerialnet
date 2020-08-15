#!/bin/bash
 
# Building packages and uploading them to a Gemfury repository
 
# Uninstall previous version of azure
#pip uninstall azure-common
#pip uninstall azure-storage
#pip uninstall azure-nspkg
#pip uninstall azure-storage-blob

set -e
 
DIRS="$@"
BASE_DIR=$(pwd)
SETUP="setup.py"
 
warn() {
    echo "$@" 1>&2
}
 
die() {
    warn "$@"
    exit 1
}
 
build() {
    DIR="${1/%\//}"
    echo "Checking directory $DIR"
    cd "$BASE_DIR/$DIR"
    [ ! -e $SETUP ] && warn "No $SETUP file, skipping" && return
    PACKAGE_NAME=$(python $SETUP --fullname)
    echo "Package $PACKAGE_NAME"
    python "$SETUP" sdist bdist_wheel || die "Building package $PACKAGE_NAME failed"
}
 
if [ -n "$DIRS" ]; then
    for dir in $DIRS; do
        build $dir
    done
else
    ls -d */ | while read dir; do
        build $dir
    done
fi

python $SETUP clean --all install 