#!/bin/sh

#Use this script to accept input bot definitions from S3 and output to a S3 bucket
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

export CONFIG_PATH=$WORKINGDIR/config.yml
export LOGSDIR=$WORKINGDIR/logs
export IN_BUCKET=s3://tradebot-in-122517
export OUT_BUCKET=s3://tradebot-out-122517

#Input section
aws s3 sync $IN_BUCKET $WORKINGDIR
if [ -f "config.yml" ]
then
	echo "config.yml found."
	python $WORKINGDIR/tradebotmanager.py $CONFIG_PATH >> $LOGSDIR/tradebotmanager.out.txt
	rm $CONFIG_PATH
	aws s3 rm $IN_BUCKET --recursive
fi

#Output section
python activebots.py > $LOGSDIR/bots.html
aws s3 sync $LOGSDIR $OUT_BUCKET > /dev/null

rm cron.lock
