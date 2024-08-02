#!/bin/sh

echo "Creating a snapshot"

if [ $# -eq 0 ]
then
    echo "Please an url as an argument."
    exit 1
fi

curl -XPUT $1

echo "Snapshot created at `date`"
