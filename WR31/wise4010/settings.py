# Email Settings
SMTP_IP = "10.173.66.124"
SMTP_PORT = 25
EMAIL_SUBJECT = "wisetest"
EMAIL_FROM = "wisetest@insight.suez.com"
EMAIL_TO = ["bhavin.gala@suez.com"] # comma separates list of strings, no spaces
POLLING_INTERVAL = 60 # Time between readings in seconds


# Devices
DEVICES = {
    "device1" : {
        "type" : "wise4010",
        "ip" : "192.168.2.5",
        "u" : 'root',
        "p" : '00000000'
    },
    "device2" : {
        "type" : "wise4012",
        "ip" : "192.168.2.6",
        "u" : 'root',
        "p" : '00000000'
    }
}