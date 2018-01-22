import yaml
import sys
import os.path
import os
import tradebot
import datetime

#prints a message with timestamp
def tprint(msg):
    now = datetime.datetime.now()
    t = now.strftime("%y-%m-%d %H:%M:%S")
    print "[" + str(t) + "] " + msg

def main(config_file_name):
    tprint("Starting bot manager with config file: %s" % config_file_name)
    logs_dir = "logs"
    tradebot_db = "trade.db"

    try:
        with open(config_file_name, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
            ymlfile.close()

    except Exception as e:
        tprint(str(e))

    for bot_name in cfg:
        logfilepath = logs_dir+"/"+bot_name+".out.txt"

        if os.path.exists(logs_dir) and os.path.exists(tradebot_db) and not os.path.isfile(logfilepath): #An output file alreade exists
            newpid = os.fork()
            if newpid == 0: #child process
                bot = tradebot.Tradebot(bot_name,cfg[bot_name],True)
                bot.run() 
                break
            else: #parent name
                tprint("INFO: TradeBotManager - Spawned %s parent pid: %d, child pid: %d\n" % (bot_name, os.getpid(), newpid))
        else:
            tprint("INFO: TradeBotManager - Skipping bot %s due to no logs directory or no trade.db; or log file exists: %s" % (bot_name,logfilepath))

 
if __name__ == "__main__":
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        tprint("ERROR: must provide a valid yaml file path")
    else:
        main(sys.argv[1])
