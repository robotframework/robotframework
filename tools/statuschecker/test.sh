#!/bin/bash

pybot --loglevel DEBUG --log none --report none example.html
python statuschecker.py output.xml
rebot output.xml


