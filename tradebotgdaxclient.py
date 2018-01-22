import tradeerrors
from hashlib import sha384
from tradebotapiclient import Tradebotapiclient
import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase

class Tradebotgdaxclient(Tradebotapiclient):

    def __init__(self, cfg):
        super(Tradebotgdaxclient, self).__init__(cfg)
        self.passphrase = cfg['passphrase']
        
    def balances(self):
        api_url = "https://" + self.base_url + "/accounts"
        auth = CoinbaseExchangeAuth(self.api_key, self.api_secret, self.passphrase)
        response = requests.get(api_url, auth=auth)
        
        if self.verbose:
            print "INFO:" + response.text

        return response.text


    def order_status(self,order_id):
        api_url = "https://" + self.base_url + "/orders/" + order_id
        auth = CoinbaseExchangeAuth(self.api_key, self.api_secret, self.passphrase)
        result = requests.get(api_url, auth=auth)
        
        if self.verbose:
            print "INFO:" + result.text

        return result 

    def cancel_order(self,order_id):
        api_url = "https://" + self.base_url + "/orders/" + order_id
        auth = CoinbaseExchangeAuth(self.api_key, self.api_secret, self.passphrase)
        result = requests.delete(api_url, auth=auth)
        
        if self.verbose:
            print "INFO:" + result.text

        return result 

    #Order type must be buy or sell
    #Returns order ID 
    #Sets the self.last_order_status and self.last_executed_amount variables
    def new_order(self,side,qty,bid):

        #Convert qty to acceptable 8 decimal digits
        qtystr = str(qty)
        dp = qtystr.find('.')
        if dp != -1:
            qtystr = qtystr[0:min(len(qtystr),dp+9)]

        #Record this attempt
        id = self.tradebotdb.preporder(self.sym,qtystr,bid)

        if id is not None:
            auth = CoinbaseExchangeAuth(self.api_key, self.api_secret, self.passphrase)
            api_url = "https://" + self.base_url + "/orders"
            req = json.dumps({
                'client_oid': str(id),
                'product_id' : self.sym,
                'size' : qtystr,
                'price' : bid,
                'side' : side,
                'type' : "limit"
            })

            result = requests.request("POST", api_url, auth=auth)
            responsetxt = result.text
            if self.verbose:
                print "INFO:" + responsetxt

            response = json.loads(responsetxt)

            self.last_executed_amount = 0
            self.last_order_status = None

            if result.status_code != 200:
                self.last_order_status = "error"
                
            elif 'id' in response and response['id'] is not None:
                order_id = response['id']

                #executed_value = usd
                #filled_size = crypto filled
                for x in range(0,2):
                    if self.evaluate_order(response) == "open":
                        time.sleep(5) #Sleep 5 seconds
                        result = self.order_status(order_id) #Check order status
                        responsetxt = result.text
                        response = json.loads(responsetxt)
                    else:
                        break
                
                if self.last_order_status == "open":
                    self.cancel_order(order_id)
                    self.last_order_status = "unsuccessful" #Issue cancel

            else:
                self.last_order_status = "unsuccessful"

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
        

        def evaluate_order(self,response):
            if 'executed_value' in response and 'filled_size' in response and 'status' in response:
                executed_amount_base = float(response['executed_value'])
                executed_amount_crypto = float(response['filled_size'])
                order_status = response['status']
                self.last_executed_amount = executed_amount_crypto

                if executed_amount_crypto > 0:
                    if order_status == "done":
                        self.last_order_status = "full"
                    else:
                        self.last_order_status = "partial"

                else: #order is in pending or open status and it should be cancelled
                    self.last_order_status = "open"

            else: #Unable to evaluate order
                self.last_order_status = "unknown"
            
            return self.last_order_status

# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.passphrase = passphrase
        self.secret_key = secret_key

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = signature.digest().encode('base64').rstrip('\n')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request
