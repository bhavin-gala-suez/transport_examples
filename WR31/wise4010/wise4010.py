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

logging.basicConfig(level = logging.INFO)

from settings import smtp_ip, smtp_port, email_to, polling_interval, devices

def isMaxSize(filename, max_size):
    return max_size > os.path.getsize(filename)

def poll_and_send(device_name, device_ip, username, password):
    t = int(round(time.time() * 1000)) # get current time in ms, pass as payload in request to get latest messages

    base64string = base64.b64encode('%s:%s' % (username, password))

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

    # logging.info(result.read())

    res = json.load(result)
    # logging.info(res['LogMsg'])
    datafile = StringIO.StringIO()
    f = csv.writer(datafile)

    # # Write CSV Header, If you dont need that, remove this line
    f.writerow(["timestamp", "ch1_D", "ch2_D", "ch3_D", "ch4_D", "ch1_A", "ch2_A", "ch3_A", "ch4_A"])

    for x in res["LogMsg"]:
        # logging.info(x)
        f.writerow([time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(x["TIM"]))),
                    x['Record'][0][3],
                    x['Record'][1][3],
                    x['Record'][2][3],
                    x['Record'][3][3],
                    x['Record'][4][3]/1000.0,
                    x['Record'][6][3]/1000.0,
                    x['Record'][8][3]/1000.0,
                    x['Record'][10][3]/1000.0
                    ])     

    contents = datafile.getvalue()
    logging.info(contents)
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = COMMASPACE.join(EMAIL_TO)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = EMAIL_SUBJECT


    part = MIMEBase('application', "octet-stream")
    part.set_payload(datafile.getvalue())
    Encoders.encode_base64(part)

    part.add_header('Content-Disposition', 'attachment; filename="'+FILENAME+'"')

    msg.attach(part)
    
    # message = "Subject: %s\n\nvalue: %s" % (EMAIL_SUBJECT, str(record))
    try:
        smtpObj = smtplib.SMTP(SMTP_IP, SMTP_PORT)
        smtpObj.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        logging.info("Successfully sent email")
    except Exception, e:
        logging.info("Failed to send. Exception: %s" %e)
        traceback.print_exc()
    return


if __name__ == '__main__':
    logging.info('Starting WISE4010 Data Logging + Transmission Application')

    count = 0
    # go = True
    # while go == True:
    #     if count == 2:
    #         go = False
    #     else:
    #         poll_and_send()
    #         count += 1
    #         time.sleep(POLLING_INTERVAL)
    while True:
        logging.info(count)
        poll_and_send()
        count += 1
        time.sleep(POLLING_INTERVAL)
    

    logging.info('======================')
    logging.info('Existing Program')
    sys.exit(0)