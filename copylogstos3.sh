#!/bin/sh

#Use this script to output logs to a S3 bucket
#Assumes this script will be run from tradebot root directory
export WORKINGDIR=$(pwd)

#echo Working directory $WORKINGDIR

#Check if a cron is already running
if [ -f "cron.lock" ]
then
    echo "Found cron.lock file, exitting"
    exit 0
else
    touch cron.lock
fi

export LOGSDIR=$WORKINGDIR/logs
export OUT_BUCKET=s3://tradebot-out-122517

#Output section
python activebots.py > $LOGSDIR/bots.html
aws s3 sync $LOGSDIR $OUT_BUCKET > /dev/null

rm cron.lock
