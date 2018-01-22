import requests
import base64
import hmac
import time
import hashlib
import json
import urllib2
import datetime
import tradebotdb
import tradeerrors
from hashlib import sha384

class Tradebotapiclient(object):

    def millis(self):
        return int(round(time.time() * 1000))

    def gemini_send(self,url,req):

        if self.verbose:
            print "INFO:" +url
            print "INFO:" +req

        b64 = base64.b64encode(req)
        signature = hmac.new(self.api_secret, b64, hashlib.sha384).hexdigest()

        headers = {
            'Content-Type': "text/plain",
            'Content-Length': "0",
            'X-GEMINI-APIKEY': self.api_key,
            'X-GEMINI-PAYLOAD': b64,
            'X-GEMINI-SIGNATURE': signature,
            'Cache-Control': "no-cache"
            }

        response = requests.request("POST", url, headers=headers)

        if self.verbose:
            print "INFO:" + response.text

        return response.text

    #Assumes first 3 letters are crypto symbol
    def getcryptoavailable(self,cryptosym):
        responsetxt = self.balances()
        response = json.loads(responsetxt)
        crypto = None

        for account in response:
            if account['currency'] == cryptosym:
                crypto = float(account['available'])
                break

        return crypto

    def getbasecurrencyavailable(self,basesym):
        responsetxt = self.balances()
        response = json.loads(responsetxt)

        base = None

        for account in response:
            if account['currency'] == basesym:
                base = float(account['available'])

        return base

    def balances(self):
        url = "https://" + self.base_url + "/v1/balances"
        req = json.dumps({
            'request': '/v1/balances',
            'nonce': self.millis()
        })
        return self.gemini_send(url,req)

    #Returns order ID, order status and executed amount
    def buy(self,qty,bid, attempts=1,step=0):
        baseavailable = self.getbasecurrencyavailable(self.sym[(len(self.sym)-3):len(self.sym)])

        if (baseavailable is not None) and (baseavailable > self.base_unit):
            id = None
            for x in range(0,attempts):
                new_bid = bid + (x*step)
                id = self.new_order("buy",qty,new_bid)
                print("INFO: order id %d, buy attempt %d, %f %s @ %f" % (id,x+1,qty,self.sym,new_bid))

                status = self.last_order_status
                if status == "full" or status == "partial":
                    break
                else: #in case of a retry, wait 5 seconds
                    if ((x+1) != attempts):
                        #sleep 5 seconds before retry
                        time.sleep(5)

            return (id,status,self.last_executed_amount)

        else: #Not enough funds available
            ief = tradeerrors.InsufficientFundsError(baseavailable,self.base_unit)
            raise(ief)

    #Returns order ID, order status and executed amount
    def sell(self,qty,bid, attempts=1,step=0):
        cryptoavailable = self.getcryptoavailable(self.sym[0:3])

        if (cryptoavailable is not None) and (cryptoavailable >= qty):
            id = None
            for x in range(0,attempts):
                new_bid = bid - (x*step)

                id = self.new_order("sell",qty,new_bid)
                print("INFO: order id %d, sell attempt %d, %f %s @ %f" % (id,x+1,qty,self.sym,new_bid))

                status = self.last_order_status
                if status == "full" or status == "partial":
                    break
                else: #in case of a retry, wait 5 seconds
                    if ((x+1) != attempts):
                        #sleep 5 seconds before retry
                        time.sleep(5)

            return (id,status,self.last_executed_amount)

        else: #Not enough funds available
            ief = tradeerrors.InsufficientFundsError(cryptoavailable,qty)
            raise(ief)

    #Order type must be buy or sell
    #Returns order ID 
    #Sets the self.last_order_status and self.last_executed_amount variables
    def new_order(self,side,qty,bid):

        #Convert qty to acceptable 8 decimal digits
        qtystr = str(qty)
        dp = qtystr.find('.')
        if dp != -1:
            if self.sym == "ETHUSD": #Accurate to 5 decimal places, otherwise gemini gives an error
                qtystr = qtystr[0:min(len(qtystr),dp+6)]
            else: #Accurate to 8 decimal places, otherwise gemini gives an error
                qtystr = qtystr[0:min(len(qtystr),dp+9)]

        #Record this attempt
        id = self.tradebotdb.preporder(self.sym,qtystr,bid)

        if id is not None:
            url = "https://" + self.base_url + "/v1/order/new"

            req = json.dumps({
                'request': '/v1/order/new',
                'nonce': self.millis(),
                'client_order_id': str(id),
                'symbol' : self.sym,
                'amount' : qtystr,
                'price' : bid,
                'side' : side,
                'type' : "exchange limit",
                'options' : ["immediate-or-cancel"]
            })

            responsetxt = self.gemini_send(url,req)
            response = json.loads(responsetxt)
            self.last_executed_amount = 0

            #Set order status based on response
            self.last_order_status = None
            if 'result' in response:
                if response['result'] == 'error':
                    self.last_order_status = "error"
                else:
                    self.last_order_status = "unknown"

            elif 'executed_amount' in response:
                executed_amount = float(response['executed_amount'])
                remaining_amount = float(response['remaining_amount'])
                self.last_executed_amount = executed_amount

                if executed_amount > 0:
                    if remaining_amount == 0:
                        self.last_order_status = "full"
                    else:
                        self.last_order_status = "partial"
                else:
                    self.last_order_status = "unsuccessful"
            else:
                self.last_order_status = "unknown"

            #update the Database with status
            self.tradebotdb.updateorder(id,self.last_order_status,responsetxt) #Update the order id with specified status
        
            #Throw an Exception in case of an error
            if self.last_order_status == "error":
                ope = tradeerrors.OrderPlacementError(responsetxt)
                raise(ope)
            
            if self.last_order_status == "unknown":
                ure = tradeerrors.UnknownResponseError(responsetxt)
                raise(ure)

        return id

    def gracefulstop(self):
        self.tradebotdb.gracefulstop()

    def __init__(self, cfg):
        self.base_url = "api." + cfg['exchange'] + ".com"
        self.api_key = cfg['api_key']
        self.api_secret = cfg['api_secret']
        self.sym = cfg['sym']
        self.base_unit = float(cfg['base_unit'])
        
        self.verbose = True

        if self.verbose:
            print("INFO: Successfully Initialized with symbol %s and exchange %s [%s]" % (self.sym,cfg['exchange'],self.base_url))
            self.tradebotdb = tradebotdb.Tradebotdb(cfg['exchange'])
