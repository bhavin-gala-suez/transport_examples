'''
Bhavin Gala - PEA237
Feb 18, 2021
'''

import sarcli
import time
import sys
import smtplib
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email.MIMEBase import MIMEBase
from email import Encoders
import StringIO
import traceback
import urllib2, base64
import json
import csv
import time
import logging
import logging.handlers

LOGFILE = "logfile"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

stdout_handler = logging.StreamHandler(sys.stdout)
# file_handler = logging.handlers.RotatingFileHandler(LOGFILE, maxBytes = 1000000, backupCount=3) # RotatingFileHandler does not work on WR21 b/c it uses windows based OS
file_handler = logging.FileHandler(LOGFILE)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(stdout_handler)
logger.addHandler(file_handler)

from settings import SMTP_IP, SMTP_PORT, EMAIL_SUBJECT, EMAIL_FROM, EMAIL_TO, POLLING_INTERVAL, DEVICES

def isMaxSize(filename, max_size):
    return max_size < os.path.getsize(filename)

def poll_and_send(device_name, device_ip, username, password):
    t = int(round(time.time() * 1000)) # get current time in ms, pass as payload in request to get latest messages

    base64string = base64.b64encode('%s:%s' % (username, password))

    try: 
        '''
        run the 'log_output' request to generate latest log messages
        '''
        request = urllib2.Request("http://%s/log_output" % device_ip)
        request.add_header("Authorization", "Basic %s" % base64string)   
        result = urllib2.urlopen(request)

        '''
        run the 'log_message' request to read latest log messages
        '''
        request = urllib2.Request("http://%s/log_message" % device_ip)
        request.add_header("Authorization", "Basic %s" % base64string)   
        result = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
        logger.exception("HTTP request failed...")


    # logger.info(result.read())

    res = json.load(result)
    # logger.info(res['LogMsg'])
    datafile = StringIO.StringIO()
    f = csv.writer(datafile)

    # # Write CSV Header, If you dont need that, remove this line
    f.writerow(["timestamp", "ch1_D", "ch2_D", "ch3_D", "ch4_D", "ch1_A", "ch2_A", "ch3_A", "ch4_A"])

    for x in res["LogMsg"]:
        # logger.info(x)
        f.writerow([x["TIM"],
                    x['Record'][0][3],
                    x['Record'][1][3],
                    x['Record'][2][3],
                    x['Record'][3][3],
                    x['Record'][4][3],
                    x['Record'][6][3],
                    x['Record'][8][3],
                    x['Record'][10][3]
                    ])     

    contents = datafile.getvalue()
    logger.debug(contents)
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = COMMASPACE.join(EMAIL_TO)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = EMAIL_SUBJECT


    part = MIMEBase('application', "octet-stream")
    part.set_payload(datafile.getvalue())
    Encoders.encode_base64(part)

    FILENAME = device_name+".csv"

    part.add_header('Content-Disposition', 'attachment; filename="'+FILENAME+'"')

    msg.attach(part)
    
    # message = "Subject: %s\n\nvalue: %s" % (EMAIL_SUBJECT, str(record))
    try:
        smtpObj = smtplib.SMTP(SMTP_IP, SMTP_PORT)
        smtpObj.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        logger.info("Successfully sent email")
    except Exception, e:
        logger.exception("Exception while trying to email file")
    return

# TODO
def validate_settings():
    pass

if __name__ == '__main__':
    logger.info('Starting WISE4000 Data Logging + Transmission Application')

    # TODO: validate settings
    # validate_settings()

    # '''
    # For testing
    # '''
    # count = 0
    # go = True
    # while go == True:
    #     if count == 1:
    #         go = False
    #     else:
    #         for k,v in DEVICES.items():
    #             try:
    #                 logger.info("Attempting poll...")
    #                 poll_and_send(k, v['ip'], v['u'], v['p'])
    #             except Exception, e:
    #                 logger.exception("Exception while trying to poll and send...")
    #     if isMaxSize(LOGFILE, 1000):
    #         logger.info("logfile full, flushing...")
    #         logger.handlers[1].stream.close()
    #         logger.removeHandler(file_handler)

    #         tmp_handler = logging.FileHandler(LOGFILE, 'w') # used to flush logfile
    #         logger.addHandler(tmp_handler)
    #         logger.info("Started new logfile...")
            
    #         logger.handlers[1].stream.close()
    #         logger.removeHandler(tmp_handler)

    #         file_handler = logging.FileHandler(LOGFILE)
    #         formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    #         file_handler.setFormatter(formatter)
    #         logger.addHandler(file_handler)
    #         logger.info("logfile flush complete...")

    #     # sleep    
    #     count += 1
    #     time.sleep(POLLING_INTERVAL)
    # '''
    # testing
    # '''

    while True:
        try:
            for k,v in DEVICES.items():
                try:
                    logger.info("Attempting poll of device: "+k)
                    poll_and_send(k, v['ip'], v['u'], v['p'])
                except Exception, e:
                    logger.exception("Exception while trying to poll and send...")

            if isMaxSize(LOGFILE, 10000000):
                logger.info("logfile full, flushing...")
                logger.handlers[1].stream.close()
                logger.removeHandler(file_handler)

                tmp_handler = logging.FileHandler(LOGFILE, 'w') # used to flush logfile
                logger.addHandler(tmp_handler)
                logger.info("Started new logfile...")
                
                logger.handlers[1].stream.close()
                logger.removeHandler(tmp_handler)

                file_handler = logging.FileHandler(LOGFILE)
                formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
                logger.info("logfile flush complete...")

            time.sleep(POLLING_INTERVAL)
        except Exception, e:
            logger.exception("Crashed... exiting program...")
            break

    logger.info('======================')
    logger.info('Existing Program')
    sys.exit(0)