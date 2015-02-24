#!/usr/bin/env bash

echo "Starting master"

vagrant up master


echo "Starting slaves"

if type parallel; then
    seq -f 'slave%g' 2 | parallel --no-notice vagrant up
else
    for i in `seq -f 'slave%g' $1`; do
        vagrant up $i
    done
fi