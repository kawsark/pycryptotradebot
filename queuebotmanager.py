import yaml
import sys
import os.path
import os
import tradebot
import datetime
import boto3
import time
import requests

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
                    tprint("INFO: Tradebot - child pid %d exitting." % os.getpid())
                    os._exit(0)
                
                else: #parent process
                    tprint("INFO: TradeBotManager - Spawned %s parent pid: %d, child pid: %d\n" % (bot_name, os.getpid(), newpid))
                    
            else: #parent process
                tprint("INFO: TradeBotManager - Skipping bot %s due to no logs directory or no data directory; or log file exists: %s" % (bot_name,logfilepath))

        #Delete message from the queue:
        message.delete()



#If this is an EC2 instance with tradebot_sqs_name tag, they use the value of that tag as queue name
def get_env_queue_name():
    sqs_tag_name = "tradebot_sqs_name"
    id_metadata_url = 'http://169.254.169.254/latest/meta-data/instance-id'

    try:
        r = requests.get(id_metadata_url, timeout=10)
        instance_id = r.text

        if instance_id is not None:
            ec2 = boto3.resource('ec2')
            ec2instance = ec2.Instance(instance_id)
            tags = ec2instance.tags

            for tag in tags:
                if tag["Key"] == sqs_tag_name:
                    sqs_tag_value = tag["Value"]
                    if sqs_tag_value is not None and len(sqs_tag_value) > 0:
                        tprint("Obtained queue name from EC2 tag: %s=%s" % (sqs_tag_name,sqs_tag_value))
                        return sqs_tag_value

    except Exception as e:
        tprint(str(e)) 
    

    tprint("Unable to obtain queue name from EC2 tag")
    return None


if __name__ == "__main__":
   config_file_name = "botserver.yml"
   try:
     with open(config_file_name, 'r') as ymlfile:
       cfg = yaml.load(ymlfile)
       ymlfile.close()
       
       #Get default queue name:
       tradebot_sqs_name = cfg['tradebot_sqs_name']

       #Try to obtain a more specific queue name from Tags
       temp = get_env_queue_name()
       if temp is not None:
           tradebot_sqs_name = temp
       
       
       # Get the service resource
       sqs = boto3.resource('sqs')

       tprint("Using queue name %s and Long polling frequency: %d" %  (tradebot_sqs_name, cfg['sqs_polling_frequency_max_20']))
       
       queue = sqs.get_queue_by_name(QueueName=tradebot_sqs_name)
       polling_frequency = cfg['sqs_polling_frequency_max_20']
       
       # Process bots:
       tprint("Listening for messages")
       while True:
           bot_messages = queue.receive_messages(MaxNumberOfMessages=10,WaitTimeSeconds=polling_frequency)
           if len(bot_messages) > 0:
               tprint("Processing %d messages: " % len(bot_messages))
               main(bot_messages)


   except Exception as e:
       tprint(str(e))

