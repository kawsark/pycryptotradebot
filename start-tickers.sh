#!/bin/bash
#Use this script to start tradebot ticker processes. To stop the processes, place a ticker.stop file in the current directory.
#This script assumes it is in the tradebot root directory
nohup python2.7 -u tickerdb.py gdax LTC-USD > logs/gdax.ltc.out.txt &
sleep 10
nohup python2.7 -u tickerdb.py gdax BTC-USD > logs/gdax.btc.out.txt &
sleep 10
nohup python2.7 -u tickerdb.py gdax ETH-USD > logs/gdax.eth.out.txt &
sleep 10
nohup python2.7 -u tickerdb.py gdax BCH-USD > logs/gdax.bch.out.txt &
sleep 10
nohup python2.7 -u tickerdb.py gemini BTCUSD > logs/gemini.btc.out.txt &
sleep 10
nohup python2.7 -u tickerdb.py gemini ETHUSD > logs/gemini.eth.out.txt &
ps -ef | grep tickerdb

