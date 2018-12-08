#!/usr/bin/env python3.6

## Import libs
from OpenSSL import SSL
from socket import socket
from datetime import datetime
import idna, requests, json, sys

## Fuction to get expire certificate date
def get_expire_date(hostname):

    ## Encode in domains with IDN compilance
    hostname_idna = idna.encode(hostname)

    ## Open and connect socket
    sock = socket()
    sock.connect((hostname, 443))

    ## Add context
    contex = SSL.Context(SSL.SSLv23_METHOD)
    contex.check_hostname = False
    contex.verify_mode = SSL.VERIFY_NONE

    ## HTTP request with SSL
    sock_ssl = SSL.Connection(contex, sock)
    sock_ssl.set_connect_state()
    sock_ssl.set_tlsext_host_name(hostname_idna)
    sock_ssl.do_handshake()

    ## Get certificate infos
    cert = sock_ssl.get_peer_certificate()
    crypto_cert = cert.to_cryptography()

    ## Close conection SSL
    sock_ssl.close()

    ## Close socket
    sock.close()

    ## Get expire date from certificate
    return crypto_cert.not_valid_after

## Function to calculate date
def calculate_date(cert_date):

    ## Get today date
    today = datetime.now()

    ## Sub between certificate date and today
    diff = cert_date.replace(tzinfo=None) - today

    ## Convert in days
    diff_in_days = int(diff.total_seconds())/86400

    ## Return diff
    return diff_in_days

## Function to generata payload for slack notification
def generatePayload(domain, expireInDays, dateExpire):
    username   = "check-ssl-robot"
    icon_emoji = ":alien:"
    channel    = "#mychannel"

    ## Message to already expire certificates
    if expireInDays < 0:
        data = {}
        data['attachments'] = [{
            'color': "danger",
            'text': "Domain: %s\nStatus: Expired\nDateExpire: %s" % (domain,dateExpire)
        }]
        data['username']    = username
        data['icon_emoji']  = icon_emoji
        data['channel']     = channel

        json_data = json.dumps(data)

    ## Message to expiring certificates
    else:
        data = {}
        data['attachments'] = [{
            'color': "warning",
            'text': "Domain: %s\nExpireInDays: %s\nDateExpire: %s" % (domain,expireInDays,dateExpire)
        }]
        data['username']   = username
        data['icon_emoji'] = icon_emoji
        data['channel']    = channel
        
        json_data = json.dumps(data)

    return json_data

## Function to send message to slack
def send_alert_slack(domain, expireInDays, dateExpire):
    ## Webhook token
    token = ""

    headers = {"Content-Type":"application/json"}
    url = "https://hooks.slack.com/services/%s" % token

    try:
        ## Send post
        requests.post(
            url,
            data=generatePayload(domain, expireInDays, dateExpire),
            headers=headers
        )
    except Exception as e:
        print("sys=check-ssl-robot log=ERROR msg=%s" %(str(e)))
        sys.exit(1)


## Function main
if __name__ == "__main__":

    ## This variable will send validate if you want to send alerts to slack
    ## If True -> Remember to configure webhook token
    send_alert = False

    ## Open file domains.conf
    f = open('domains.conf')

    for line in f:
        ## Remove spaces
        domain = "".join(line.split())
        try:
            ## Exec func to get expire date
            cert_date = get_expire_date(domain)
        except Exception as e:
            print("sys=check-ssl-robot log=ERROR domain=%s msg=%s" %(domain, str(e)))

        ## Exec func to calculate dates
        cert_date_diff = int(calculate_date(cert_date))

        ## Define 30 days to send a alert to exping certificates
        if cert_date_diff <= 30 and cert_date_diff >= 1:
            print("sys=check-ssl-robot log=WARN domain=%s expireInDays=%s state=Expiring dateExpire=%s" %(domain, cert_date_diff, cert_date))
            if send_alert:
                send_alert_slack(domain, cert_date_diff, cert_date)
        elif cert_date_diff <= 0:
            print("sys=check-ssl-robot log=WARN domain=%s state=Expired dateExpire=%s" %(domain, cert_date))
            if send_alert:
                send_alert_slack(domain, cert_date_diff, cert_date)

    ## Close file domains.conf
    f.close()