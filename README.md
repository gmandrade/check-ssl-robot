# check-ssl-robot

## Requiremets
* Python version 3.6
* Pip version >= 3
* pyopenssl version 18.0.0
* idna version 2.6
* requests version 2.20.1

```bash
pip3 install -r requirements.txt
```

## ADD domain to check
* Edit `domains.conf` add a domain per line

## Engine
Function `get_expire_date`:
* Open a socket connection
* Get SSL/TLS infos
* Return certificate date

Function `calculate_date`:
* Calculate date between expire date and D0

Function `generatePayload`:
* Generate a payload to send a message in slack

Function `send_alert_slack`:
* Get domain, diff between dates and expire date
* Send the message to slack

Função `main`:
* Open `domains.conf`
* Execute `get_expire_date` and `calculate_date` in all lines
* OPTIONAL - Send a message in slack
* Ouput a domais with 30 days to expire certificate

## Usability

```bash
$ ./main.py
sys=check-ssl-robot log=WARN domain=example.com expireInDays=30 state=Expiring dateExpire=2019-01-08 23:59:59
sys=check-ssl-robot log=WARN domain=example2.com expireInDays=25 state=Expiring dateExpire=2019-01-03 23:59:59
sys=check-ssl-robot log=WARN domain=example3.com state=Expired dateExpire=2018-01-03 23:59:59
```