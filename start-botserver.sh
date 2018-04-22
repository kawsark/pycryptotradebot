#!/bin/bash
#Use this script to start tradebot queue server process. 
#This script assumes it is in the tradebot root directory
nohup python2.7 -u queuebotmanager.py > logs/tradebotmanager.out.txt 2> logs/tradebotmanager.err.txt &
