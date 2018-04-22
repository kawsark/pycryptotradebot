import tradebotapiclient
import tradebotgdaxclient
import tickerdb
import math
import time
import datetime
import traceback
import random
import yaml
import sys
import os.path
import tradeerrors
import os

class Tradebot(object):

    def issuebuyorder(self,current):
        cryptotobuy = self.base_unit / current
        self.buyrate = current
        id = None
        i = len(self.sym)-3
        j = len(self.sym)
        if self.dryrun:
            self.tprint("NOOP: Issuing buy order for %f %s at %f %s" % (cryptotobuy,self.sym[0:3],self.buyrate,self.sym[i:j]))
            id = 0
        else:
            self.tprint("Issuing buy order for %f %s at %f %s" % (cryptotobuy,self.sym[0:3],self.buyrate,self.sym[i:j]))
            id, status, executed_amount = self.tradebotapiclient.buy(cryptotobuy,current,4,10)
            if id is not None:
                self.tprint("Buy order %f has status: %s" % (id,status))

                if status == "full" or status == "partial": #Buy was successful
                    self.crypto_bought = executed_amount 
                    self.tprint("Bought crypto amount %f " % self.crypto_bought)
                else: #in case of a failure perform random backoff
                    self.errorwithrandombackoff(self.interval,300)
                    id = None
        return id

    def issuesellorder(self,current):
        cryptotosell = self.base_unit / current
        self.sellrate = current
        id = None
        i = len(self.sym)-3
        j = len(self.sym)
        if self.dryrun:
            self.tprint("NOOP: Issuing sell order for %f %s at %f %s" % (cryptotosell,self.sym[0:3],self.sellrate,self.sym[i:j]))
            id = 0
        else:
            self.tprint("NOOP: Issuing sell order for %f %s at %f %s" % (cryptotosell,self.sym[0:3],self.sellrate,self.sym[i:j]))
            id, status, executed_amount = self.tradebotapiclient.sell(cryptotosell,current,4,10)
            if id is not None:
                self.tprint("Sell order %f has status: %s" % (id,status))
            
                if status == "full" or status == "partial": #Sell was successful
                    self.crypto_sold = executed_amount 
                    self.tprint("Sold crypto amount %f " % self.crypto_sold)
                    if self.crypto_bought is not None:
                        crypto_new = self.crypto_bought - self.crypto_sold
                        self.tprint("Crypto added since previous buy: %f " % crypto_new)
                        self.crypto_added = self.crypto_added + crypto_new
                        self.tprint("Total crypto added: %f " % self.crypto_added)

                else: #in case of a failure perform random backoff
                    self.errorwithrandombackoff(self.interval,300)
                    id = None
        return id

    #State changes for auto mode. Override for other modes
    def nextstate(self):
        if self.state == 0: #prebuy
            if self.botparmsdict['trailing_buy_percent'] > 0:
                self.state = 1 #buy or auto mode
            else:
                if self.mode == "auto": #mode is auto and trailing_percent == 0
                    self.state = 2
                else: #mode is buy and trailing_percent == 0
                    self.iterations = self.iterations + 1

        elif self.state ==1: #trailingbuy
            if self.mode == "buy":
                self.iterations = self.iterations + 1
                self.state = 0
            else: #mode is auto
                self.state = 2

        elif self.state ==2: #presell
            if self.botparmsdict['trailing_sell_percent'] > 0:
                self.state = 3 #sell or auto mode
            else: 
                self.iterations = self.iterations + 1
                if self.mode == "auto":
                    self.state = 0 #mode is auto and trailing_percent == 0
                else:
                    pass #mode is sell and trailing_percent == 0
                
        elif self.state == 3: #trailingsell
            self.iterations = self.iterations + 1
            if self.mode == "sell":
                self.state = 2 #Go back to pre-sell
            else: #Mode is auto - go back to beginning
                self.state = 0

        if self.iterations >= self.iterations_to_live:
            self.state = -1
            self.tprint("Tradebot stopping, reached iterations to live")
            self.interval = 0.5
            return
        else:
            self.interval = self.intervals[self.state_names[self.state]]
    
    def run(self):
        self.errorcount = 0
        self.fatalerrors = 0 
        self.maxfatalerrors = 3 
        self.maxconterrors = 15 #If there are 10 continuous errors then we should quit
        self.conterrors = 0
        self.crypto_added = 0

        self.tprint("Tradebot starting, output key: [State: %s| Iteration: %d]" % (self.state_names[self.state],self.iterations))

        while True:
            try:
                if self.state == -1: #Stopping if this flag is set
                    break

                if os.path.isfile(self.stopfilename) or os.path.isfile(self.globalstopfilename): #stop if this file is found
                    self.tprint("Stopping due to presence of stopfile: %s, or global stopfile: %s" % (self.stopfilename, self.globalstopfilename))
                    break
                
                current = self.tickerdb.last(self.sym)
                
                if self.state == 0: #prebuy state
                    base_value = self.base_value_method(self.sym)
                    delta = self.getabsbasedelta(current,base_value,"current",self.botparmsdict['base_value'])
                
                    if current < base_value and  delta >= self.botparmsdict['buy_delta_percent']:
                        if self.botparmsdict['trailing_buy_percent'] == 0: #issue immediate buy
                            if self.issuebuyorder(current) is not None:
                                self.nextstate()

                        else: #trigger trailing stop buy state
                            self.trailing_buy_low = current
                            self.trailing_buy_high = current * (100 + self.botparmsdict['trailing_buy_percent'])/100
                            self.nextstate()

                elif self.state == 1: #trailing stop buy state
                    base_value = self.base_value_method(self.sym)
                    delta = self.getabsbasedelta(current,base_value,"current",self.botparmsdict['base_value'])

                    if current < self.trailing_buy_low:
                        self.trailing_buy_low = current
                        self.trailing_buy_high = current * (100 + self.botparmsdict['trailing_buy_percent'])/100
                    elif current > self.trailing_buy_high and current < base_value:
                        if self.issuebuyorder(current) is not None:
                            self.nextstate()

                elif self.state == 2: #presell
                    delta = self.getabsbasedelta(current,self.buyrate,"current","buy rate")
                    
                    if current > self.buyrate and delta >= self.botparmsdict['sell_delta_percent']:
                        if self.botparmsdict['trailing_sell_percent'] == 0: #issue immediate sell
                            if self.issuesellorder(current) is not None:
                                self.nextstate()

                        else: #trigger trailing stop sell
                            self.trailing_sell_high = current
                            self.trailing_sell_low = current * (100 - self.botparmsdict['trailing_sell_percent'])/100
                            self.nextstate()

                elif self.state == 3: #trailing stop sell state
                    delta = self.getabsbasedelta(current,self.buyrate,"current","buy rate")

                    if current > self.trailing_sell_high:
                        self.trailing_sell_high = current
                        self.trailing_sell_low = current * (100 - self.botparmsdict['trailing_sell_percent'])/100
                    elif current < self.trailing_sell_low and current > self.buyrate:
                        if self.issuesellorder(current) is not None:
                            self.nextstate()
                

                if self.conterrors > 0: #Reset continuous errors to zero
                    self.conterrors = 0

                time.sleep(self.interval)
            
            except tradeerrors.InsufficientFundsError as ife: #Exit immediately
                self.tprint(str(ife))
                traceback.print_exc()
                break
                
            except tradeerrors.OrderPlacementError as ope: #Try backing off with 3 retries max
                self.tprint(str(ope))
                traceback.print_exc()
                if self.fatalerrors < self.maxfatalerrors:
                    self.fatalerrors = self.fatalerrors + 1 
                    self.errorwithrandombackoff(self.interval+300,300)
                else:
                    self.tprint("Exiting due to reaching maximum # of fatal errors: %d" % self.maxfatalerrors)
                    break
                
            except tradeerrors.UnknownResponseError as ure: #Try backing off with 3 retries max
                self.tprint(str(ure))
                traceback.print_exc()
                if self.fatalerrors < self.maxfatalerrors:
                    self.fatalerrors = self.fatalerrors + 1 
                    self.errorwithrandombackoff(self.interval+300,300)
                else:
                    self.tprint("Exiting due to reaching maximum # of fatal errors: %d" % self.maxfatalerrors)
                    break

            except Exception as e: #General errors: log and keep going
                self.tprint(str(e))
                traceback.print_exc()
                if self.conterrors < self.maxconterrors:
                    self.conterrors = self.conterrors + 1
                    self.errorwithrandombackoff(self.conterrors*self.interval,100)
                else:
                    self.tprint("Exiting due to reaching maximum # of continuous errors: %d" % self.maxconterrors)
                    break

        self.tradebotapiclient.gracefulstop()
                

    def errorwithrandombackoff(self,minimum,randomrange):
        self.errorcount = self.errorcount + 1
        backofftime = minimum + random.randint(0,randomrange)
        self.tprint("ERROR: Error count %d, pausing for %d seconds" % (self.errorcount,backofftime) )
        time.sleep(backofftime)

    def getabsbasedelta(self,val,base,val_desc,base_desc):
        cmp = "+"
        if val < base:
            cmp = "-"

        delta = ((math.fabs(val-base) / base)*100)
        roc = delta - self.prevdelta
        self.prevdelta = delta

        self.tprint("%s [%f], %s [%f], delta: %s%f%% (roc: %f)" % (val_desc,val,base_desc,base,cmp,delta,roc))
        return delta

    #prints a message with state and timestamp
    def tprint(self,msg):
        now = datetime.datetime.now()
        t = now.strftime("%y-%m-%d %H:%M:%S")
        print("[%s][%s|%d] %s" % (str(t),self.state_names[self.state],self.iterations,msg))

    def get_base_value(self,sym):
        return self.base_value

    def __init__(self, bot_name, cfg, redirect_output):
        self.bot_name = bot_name
        self.state_names = ['prebuy','trailing_buy','presell','trailing_sell']
        
        #Redirecting output
        if redirect_output: 
            logs_dir = "logs"
            out_path = logs_dir + "/" + bot_name + ".out.txt"
            err_path = logs_dir + "/" + bot_name + ".err.txt"

            if os.path.exists(logs_dir) and not os.path.exists(out_path) and not os.path.exists(err_path):
                print("NOTE: Redirecting stderr to %s, and stdout to: %s" % (err_path,out_path)) #Not using tprint as state has not been established
                sys.stdout = open(out_path, 'w')
                sys.stderr = open(err_path, 'w')
                #Set streams to unbuffered
                sys.stdout = Unbuffered(sys.stdout)
                sys.stderr = Unbuffered(sys.stderr)
            else: #Not using tprint as state has not been established
                msg = "ERROR: Logs directory: %s does not exist, or log files: %s %s exist" % (logs_dir,out_path,err_path)
                print(msg)
                e = tradeerrors.BotIniterror(msg)
                raise(e)
        
        #Enable safemode by default or in case of missing api credentials
        if 'safemode' not in cfg or 'api_key' not in cfg or 'api_secret' not in cfg: 
            cfg['safemode'] = True
        elif cfg['safemode'] == True and cfg['exchange'] == "gdax" and 'passphrase' not in cfg:
            cfg['safemode'] = True
        else:
            pass

        #In case of safemode clear out credentials from memory
        if cfg['safemode']:
            cfg['passphrase'] = None
            cfg['api_key'] = None
            cfg['api_secret'] = None

        #Handle required parameters
        self.botparmsdict = {
            'sym': cfg['sym'],
            'exchange': cfg['exchange'],
            'dryrun': bool(cfg['safemode']),
            'base_unit': float(cfg['base_unit']),
            'mode': cfg['mode'],
            'base_value': cfg['base_value'],
            'trailing_buy_percent': cfg['trailing_percent'],
            'trailing_sell_percent': cfg['trailing_percent'],
        }
        
        #Populate required parameters
        self.sym = self.botparmsdict['sym']
        self.base_unit = self.botparmsdict['base_unit']
        self.dryrun = self.botparmsdict['dryrun']
        self.mode = self.botparmsdict['mode']

        if self.mode == "auto" or self.mode == "sell":
            self.botparmsdict['sell_delta_percent'] = float(cfg['sell_delta_percent'])
        
        if self.mode == "auto" or self.mode == "buy":
            self.botparmsdict['buy_delta_percent'] = float(cfg['buy_delta_percent'])

        if self.mode == "sell":
            self.botparmsdict['prev_purchase_val'] = float(cfg['prev_purchase_val'])

        #Handle optional parameters
        if 'iterations_to_live' not in cfg:
            self.botparmsdict['iterations_to_live'] = 3
        else:
            self.botparmsdict['iterations_to_live'] = int(cfg['iterations_to_live'])

        if 'default_interval' not in cfg:
            self.botparmsdict['default_interval'] = 60
        else:
            self.botparmsdict['default_interval'] = int(cfg['default_interval'])

        if 'trailing_interval' not in cfg:
            self.botparmsdict['trailing_interval'] = 10
        else:
            self.botparmsdict['trailing_interval'] = int(cfg['trailing_interval'])

        #populate optional parameters
        self.interval = self.botparmsdict['default_interval']
        self.iterations_to_live = self.botparmsdict['iterations_to_live']
        
        #Instantiate API Client
        exchange = cfg['exchange']
        if exchange == 'gdax':
            self.tradebotapiclient = tradebotgdaxclient.Tradebotgdaxclient(cfg) 
            self.tickerdb = tickerdb.Tickerdb("gdax",self.sym)
        elif exchange == 'gemini':
            self.tradebotapiclient = tradebotapiclient.Tradebotapiclient(cfg) 
            self.tickerdb = tickerdb.Tickerdb("gemini",self.sym)
        else:
            e = tradeerrors.InputError(exchange,"exchange")
            raise(e)

        #handle base_value parameter:
        base_value = cfg['base_value']
        if base_value == "daily_avg":
            self.base_value_method = self.tickerdb.getDailyAverage
        elif base_value == "weekly_avg":
            self.base_value_method = self.tickerdb.getWeeklyAverage
        elif base_value == "hourly_avg":
            self.base_value_method = self.tickerdb.getHourlyAverage
        elif base_value == "monthly_avg":
            self.base_value_method = self.tickerdb.getMonthlyAverage
        else: #A static value was set
            self.base_value = float(base_value)
        
            if self.mode == "buy":
                self.base_value_method = self.get_base_value
            else:
                self.tprint("ERROR: A static base_value is only allowed with buy modes")
                e = tradeerrors.InputError(str(self.base_value),"base_value")
                raise(e)

        #set initial state        
        self.iterations = 0
        self.stopfilename = self.bot_name+".stop"
        self.globalstopfilename = "bot.stop"
        self.prevdelta = 0

        if self.mode == "auto" or self.mode == "buy":
            self.state = 0
        elif self.mode == "sell":
            self.buyrate = self.botparmsdict['prev_purchase_val']
            self.state = 2
            self.crypto_bought = self.base_unit / self.buyrate
        else:
            e = tradeerrors.InputError(self.mode,"mode")
            raise(e)


        self.tprint("INFO: Successfully Initialized Tradebot instance with bot_name %s and parameter set %s " % (self.bot_name,self.botparmsdict))
        self.tprint("INFO: To stop, create an empty file called in current directory: %s" % self.stopfilename)

        if self.dryrun:
            self.tprint("INFO: SAFEMODE (DRYRUN) IS ON. No buy or sell orders will be issued.")
        else:
            self.tprint("WARNING: SAFEMODE (DRYRUN) IS OFF, WILL ISSUE BUY / SELL ORDERS, CONSIDER RISK OF LOSS!")

        self.intervals = {
            'prebuy': self.botparmsdict['default_interval'],
            'trailing_buy': self.botparmsdict['trailing_interval'],
            'presell': self.botparmsdict['default_interval'],
            'trailing_sell': self.botparmsdict['trailing_interval']
        }


#A class to flush output on every print
#https://stackoverflow.com/questions/107705/disable-output-buffering
class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)


#Main method to run without a tradebot manager
def main(bot_name):
    config_file_name = "config.yml"

    try:
        with open(config_file_name, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
            ymlfile.close()
            bot = Tradebot(bot_name,cfg[bot_name],False)
            bot.run()
 
    except Exception as e:
        print(str(e))
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: must provide a bot name from config.yml")
    else:
        main(sys.argv[1])
