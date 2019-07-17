#!/bin/bash

./run.py -i $1 -g smallerOutputFile
mv results/$1.json stp_domains/test/
./stpTrainer_unittest.py
