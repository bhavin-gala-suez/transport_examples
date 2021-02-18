#!/usr/bin/Python
import os
import sys
import smtplib
import traceback
##########################################################################
##########################################################################
# '''###PROVIDE INPUTS HERE###'''
EMAIL_HOST = "10.173.66.124"
sender = 'wr31@insight.suez.com' #ANY NAME
# Receivers email id
receivers = ['bhavin.gala@suez.com','iversona709@gmail.com']
message = """ From: Digi Sample <M2M@digi.com>
To: <first_name.lastname@digi.com>,<second_name.last_name@digi.com>
CC: <first_name.lastname@digi.com>
Subject: SMTP e-mail test
This is a test e-mail
"""
##########################################################################
##########################################################################
try:
    smtpObj = smtplib.SMTP(EMAIL_HOST, 25)
    smtpObj.sendmail(sender, receivers, message)
    print "Successfully sent email"
except Exception, e:
    print "Exception %s" %e
    traceback.print_exc()
print "End of the program"