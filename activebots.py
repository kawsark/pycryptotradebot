import os
import time
import sys

def main(logs_dir):
    listing = os.listdir(logs_dir)
    tickers = ['gdax.eth.out.txt','gdax.btc.out.txt','gdax.ltc.out.txt','gdax.bch.out.txt','gemini.btc.out.txt','gemini.eth.out.txt','tickerdb.eth.out.txt','tickerdb.btc.out.txt']
    inactive = []
    active = []

    print("<html><head><title>Bot listing</title></head><body>")
    print("<h2>Tradebot Manager</h2>")

    for f in listing:
        fp = logs_dir + "/" + f
        if f not in tickers and os.path.isfile(fp) and fp.endswith("out.txt"):
            tf = os.path.getmtime(fp)
            t = time.time()
            td = t - tf
            if td < 300:
                active.append(f)
            else:
                inactive.append(f)

    print("<h3>Active Bots (%d)</h3>" % len(active))
    for f in active:
        print("<a href=\"/%s\">%s</a><br>"%(f,f))

    print("<h3>Ticker Bots (%d)</h3>" % len(tickers))
    for f in tickers:
        print("<a href=\"/%s\">%s</a><br>"%(f,f))

    print("<h3>InActive Bots (%d)</h3>" % len(inactive))
    for f in inactive:
        print("<a href=\"/%s\">%s</a><br>"%(f,f))

    print("</body></html>")

if __name__ == "__main__":
    logs_dir = 'logs'
    if len(sys.argv) >= 2:
        logs_dir = sys.argv[1]

    main(logs_dir)

