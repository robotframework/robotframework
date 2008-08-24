#!/bin/bash

cd $(dirname $0)

for doc in */doc/*.txt; do
    python tooldoc2html.py $doc
done
