import yaml
import sys
import os.path
import os
import tradebot
import datetime
import boto3
import time

#prints a message with timestamp
def tprint(msg):
    now = datetime.datetime.now()
    t = now.strftime("%y-%m-%d %H:%M:%S")
    print "[" + str(t) + "] " + msg

def main(bot_messages):
    logs_dir = "logs"
    data_dir = "data"

    for message in bot_messages:
        bot_cfg = yaml.load(message.body)
        tprint("Processing %d bots: " % len(bot_cfg))
        
        for bot_name in bot_cfg:
            logfilepath = logs_dir+"/"+bot_name+".out.txt"

            if os.path.exists(logs_dir) and os.path.exists(data_dir) and not os.path.isfile(logfilepath): #An output file alreade exists
                newpid = os.fork()
                if newpid == 0: #child process
                    bot = tradebot.Tradebot(bot_name,bot_cfg[bot_name],True)
                    bot.run() 
                    break
                
                else: #parent process
                    tprint("INFO: TradeBotManager - Spawned %s parent pid: %d, child pid: %d\n" % (bot_name, os.getpid(), newpid))
                    
            else: #parent process
                tprint("INFO: TradeBotManager - Skipping bot %s due to no logs directory or no data directory; or log file exists: %s" % (bot_name,logfilepath))

            #Delete message from the queue:
            message.delete()


if __name__ == "__main__":
   config_file_name = "botserver.yml"
   try:
     with open(config_file_name, 'r') as ymlfile:
       cfg = yaml.load(ymlfile)
       ymlfile.close()
       
       # Get the service resource
       sqs = boto3.resource('sqs')

       tprint("Using queue name %s, and sqs_polling_frequency: %d" %  (cfg['tradebot_sqs_name'],cfg['sqs_polling_frequency']))
       
       queue = sqs.get_queue_by_name(QueueName=cfg['tradebot_sqs_name'])
       polling_frequency = cfg['sqs_polling_frequency']
       
       # Process bots:
       tprint("Listening for messages")
       while True:
           bot_messages = queue.receive_messages(MaxNumberOfMessages=1)
           if len(bot_messages) > 0:
               tprint("Processing %d messages: " % len(bot_messages))
               main(bot_messages)

           #Sleep for polling_frequency:
           time.sleep(polling_frequency)

   except Exception as e:
       tprint(str(e))

