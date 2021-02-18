# Modified version of wr31Vin_email from https://github.com/digidotcom/transport_examples.git 
# Sends data to InSight via email


############################################################################
#                                                                          #
# This Source Code Form is subject to the terms of the Mozilla Public      #
# License, v. 2.0. If a copy of the MPL was not distributed with this      #
# file, You can obtain one at http://mozilla.org/MPL/2.0/.                 #
#                                                                          #
# Copyright (c)2017 Digi International Inc. All Rights Reserved.           #
#                                                                          #
############################################################################

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

# User Configurable Settings 
SMTP_IP = "205.173.88.124"
SMTP_PORT = 25
EMAIL_SUBJECT = "wr31_test_victor"
EMAIL_FROM = "wr31@insight.suez.com"
EMAIL_TO = ["bhavin.gala@suez.com"] # list of strings
FILENAME = 'wr31.csv'

POLLING_INTERVAL = 600 # Time between readings in seconds
ANALOG_CHANNEL = 'current' # current or voltage

# System Variables
CMD_DIO = 'gpio dio'
CMD_AIN = 'gpio ain'
ANALOG_CHANNEL_CONTROLS = ['current', 'voltage']
DIGITAL_CHANNELS = ['D0', 'D1']
DIGITAL_IO_OPTIONS = ['on', 'off']

# Your python code can detect when it is running on a Transport product by
# importing the 'sys' module, then testing the sys.platform variable like this:
if sys.platform == 'digiSarOS':
    print "\nRunning on Digi Transport"

def cli(command):
    s = sarcli.open()
    s.write(command)
    resp = s.read()
    s.close()  # Close sarcli session
    return resp

def check_analog_control(control):
    """
    Validate the requested analong control is a valid analong control for
    the WR31
    """
    if control not in ANALOG_CHANNEL_CONTROLS:
        print 'Invalid analog control type:'
        print 'controls: {0}'.format(ANALOG_CHANNEL_CONTROLS)
        return False
    return True

def check_digital_channel(channel):
    """
    Validate the requested digital channel is a valid digital channel for
    the WR31
    """
    if channel not in DIGITAL_CHANNELS:
        print 'Channels: ' + str(DIGITAL_CHANNELS)
        return False
    return True

def parse_gpio_response(response_str):
    lines = response_str.strip().splitlines()
    lines.remove('OK')
    i = 0
    for line in lines:
        newline = line.split(": ")
        del lines[i]
        lines.insert(i, newline)
        i += 1
    return lines

def set_analog_io_type(io_type):
    command = '{0} {1}'.format(CMD_AIN, io_type)
    if check_analog_control(io_type):
        print parse_gpio_response(cli(command))
        print 'Analog set to {0}'.format(io_type)
        return True
    return False

def read_gpio_analog(io_type):
    """
    Parse Analog Value
    >gpio ain [current]
    A0: current=0.0173 mA
    OK
    ----
    >gpio ain [voltage]
    A0: voltage=0.0075 V
    OK
    """
    timestamp = time.strftime('%m/%d/%Y %H:%M')
    resp = cli('gpio ain')
    print resp
    if io_type == 'current':
        i = resp.find('current=')
        j = resp.find('mA')
        val = float(resp[i+8:j-1])
    elif io_type == 'voltage':
        i = resp.find('voltage=')
        j = resp.find('V')
        val = float(resp[i+8:j-1])
    record = {'timestamp': timestamp, 'val': val}
    print record
    return record

# TODO: complete implemention
def read_gpio_digital():  
    """
    Parse Digital Channel Response to a value (0 or 1)
    Read Digital Channel Response
    >gpio dio
    D0: DOUT=OFF, DIN=HIGH (Inactive)
    D1: DOUT=OFF, DIN=HIGH (Inactive)
    OK
    """ 
    return val

# def poll_and_send():
#     val = read_gpio_analog(ANALOG_CHANNEL)
#     message = "Subject: %s\n\nvalue: %d" % (EMAIL_SUBJECT, val)
#     try:
#         smtpObj = smtplib.SMTP(SMTP_IP, SMTP_PORT)
#         smtpObj.sendmail(EMAIL_FROM, EMAIL_TO, message)
#         print "Successfully sent email"
#     except Exception, e:
#         print "Failed to send. Exception: %s" %e
#         traceback.print_exc()
#     return

def poll_and_send():
    record = read_gpio_analog(ANALOG_CHANNEL)

    datafile = StringIO.StringIO()
    datafile.write('timestamp,ch1\n')
    datafile.write(record['timestamp']+','+str(record['val']))
    contents = datafile.getvalue()
    print contents


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
        print "Successfully sent email"
    except Exception, e:
        print "Failed to send. Exception: %s" %e
        traceback.print_exc()
    return


if __name__ == '__main__':
    print 'Starting GPIO Data Logging + Transmission Application'

    if not check_analog_control(ANALOG_CHANNEL):
        print 'Existing Program'
        sys.exit(0)
    else:
        set_analog_io_type(ANALOG_CHANNEL)

        # count = 0
        # go = True
        # # spin forever
        # while go == True:
        #     if count == 2:
        #         go = False
        #     else:
        #         poll_and_send()
        #         count += 1
        #         time.sleep(POLLING_INTERVAL)

        # spin forever
        while True:
            poll_and_send()
            time.sleep(POLLING_INTERVAL)

    print '======================'
    print 'Existing Program'
    sys.exit(0)