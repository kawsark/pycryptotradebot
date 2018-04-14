#!/bin/sh

#Use this script to perform Database and logs backups
#This script assumes it is in the tradebot root directory

echo Maintenance starting - warning all ticker and bots will be stopped
echo Current working directory is: $(pwd)
mkdir -p archives
sleep 10

echo Displaying processes
ps -ef | grep tickerdb
ps -ef | grep tradebot

#Database maintenance:
touch ticker.stop
touch bot.stop
echo Going to sleep for 90 seconds to stop all tradebot processes
sleep 90

echo Displaying processes
ps -ef | grep tickerdb
ps -ef | grep tradebot

cd data/
python2.7 backupdb.py
cd ../
mv data/*db-backup* archives/
#Logs maintenance:
zip tradebot.logs.$(date +%s).zip logs/*
mv *tradebot.logs* archives/

echo resuming tickers
#Start tickers
rm ticker.stop
rm bot.stop
./start-tickers.sh

echo Maintenance complete
