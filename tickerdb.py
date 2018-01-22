import sqlite3
import datetime
import sys
import random
import urllib2
import json
import traceback
from time import sleep
import os.path
from sqlite3 import Error
import tradeerrors

class Tickerdb:

    def gemini_ticker_last(self,sym):
        url = "https://api.gemini.com/v1/pubticker/" + sym.lower()
        response = urllib2.urlopen(url)
        responsejson = json.loads(response.read())

        if 'last' in responsejson:
            return float(responsejson['last'])

        return None

    def gdax_ticker_last(self,sym):
        url = "https://api.gdax.com/products/" + sym.lower() + "/ticker"
        response = urllib2.urlopen(url)
        responsejson = json.loads(response.read())

        if 'price' in responsejson:
            return float(responsejson['price'])

        return None

    def insertValue(self,timestamp,sym,value):
        cursor = self.conn.cursor()
        c1 = cursor.execute("insert into ticker (DATE, SYM, VALUE) values (?,?,?)", (timestamp,sym,value) )
        self.conn.commit()

    def getHourlyAverage(self,sym):
        t = datetime.datetime.now()
        td = datetime.timedelta(hours=1)
        t1 = t - td
        t1str = t1.strftime("%y-%m-%d %H:%M:%S.%f")
        return self.getAverage(t1str,sym)

    def getMinuteAverage(self,sym):
        t = datetime.datetime.now()
        td = datetime.timedelta(minutes=1)
        t1 = t - td
        t1str = t1.strftime("%y-%m-%d %H:%M:%S.%f")
        return self.getAverage(t1str,sym)

    def getDailyAverage(self,sym):
        t = datetime.datetime.now()
        td = datetime.timedelta(hours=24)
        t1 = t - td
        t1str = t1.strftime("%y-%m-%d %H:%M:%S.%f")
        return self.getAverage(t1str,sym)

    def getWeeklyAverage(self,sym):
        t = datetime.datetime.now()
        td = datetime.timedelta(weeks=1)
        t1 = t - td
        t1str = t1.strftime("%y-%m-%d %H:%M:%S.%f")
        return self.getAverage(t1str,sym)

    def getAverage(self,timeafterstr,sym):
        cursor = self.conn.cursor()
        c1 = cursor.execute('''select AVG(VALUE) from ticker WHERE DATE > ? AND SYM = ?''', (timeafterstr,sym))
        return c1.fetchone()[0]

    def __init__(self,exchange,sym):
        self.conn = None
        self.exchange = exchange
        self.sym = sym
        
        if self.exchange == "gemini":
            self.last = self.gemini_ticker_last
        elif self.exchange == "gdax":
            self.last = self.gdax_ticker_last
        else:
            e = tradeerrors.InputError(self.exchange,"exchange")
            raise(e)
        
        db_file = "data/ticker-" + self.exchange + ".db"
        try:
            self.conn = sqlite3.connect(db_file)
            print("INFO: Successfully initialzied Tickerdb with db_file %s" % db_file)

        except Error as e:
            print("ERROR: could not initialize Tickerdb")
            print(e)


    def run(self,interval):
        stopfilename = "ticker.stop"
        x = 0
        errorcount = 0
        conterrors = 0

        while True:
            now = datetime.datetime.now()
            t = now.strftime("%y-%m-%d %H:%M:%S.%f")
            t1 = now.strftime("%y-%m-%d %H:%M:%S")

            if os.path.isfile(stopfilename): #stop if this file is found
                print("[%s] Stopping due to presence of stopfile: %s" % (str(t1),stopfilename))
                self.conn.close()
                break

            try:
                val = self.last(self.sym)
                self.insertValue(t,self.sym,val)

                print("[%s]" % x)
                print("[%s] %s %s last: %f" % (str(t1),self.exchange,self.sym,val))
                print("[%s] Daily average: %f" % (str(t1),self.getDailyAverage(self.sym)) )
                print("[%s] Hourly average: %f" % (str(t1),self.getHourlyAverage(self.sym)) )
                x += 1
                
                if conterrors > 0:
                    conterrors = 0
                
                sleep(interval)

            except Exception as e:
                print str(e)
                traceback.print_exc()
                errorcount += 1
                backofftime = (conterrors*interval) + random.randint(0,interval)

                print ("INFO: Error count %d, continuous %d, Retrying in %d seconds" % (errorcount,conterrors,backofftime) )
                sleep(backofftime)
                conterrors += 1
                

def main(exchange, sym, interval = 60):
    if interval < 5:
        print("ERROR: Interval must be 5 seconds or higher")
        return
    
    tickerdb = Tickerdb(exchange, sym)
    tickerdb.run(interval)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("ERROR: must provide Exchange name (gemini | gdax) and symbol (BTCUSD, LTC-USD etc.)")
    else:
        main(sys.argv[1],sys.argv[2],60)
