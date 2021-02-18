# Email Settings
smtp_ip = "10.173.66.124"
smtp_port = 25
email_to = ["insightmail@insight.suez.com", "bhavin.gala@suez.com"] # comma separates list of strings, no spaces
polling_interval = 600 # Time between readings in seconds


# Devices
devices = {
    "device1" : {
        type = "wise4010",
        ip = "10.0.0.1",
        u = 'root',
        p = '00000000'
    },
    "device2" : {
        type = "wise4010",
        ip = "10.0.0.2"
    }
}