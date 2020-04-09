import os
import requests
from datetime import datetime, timedelta

SITE = os.environ['site']  # URL of the site to check, stored in the site environment variable
EXPECTED = os.environ['expected']  # http code expected
APIKEY = os.environ['apiKey']
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
querystring = {"startDate": yesterday, "endDate": yesterday}
headers = {
    'accept': "application/json",
    'api-key': APIKEY
}

def validate(res):
    '''Return False to trigger the canary

    Currently this simply checks whether the EXPECTED string is present.
    However, you could modify this to perform any number of arbitrary
    checks on the contents of SITE.
    '''
    return EXPECTED in res


def percentage(a, b):
    return round(a / b * 100, 2)


def lambda_handler(event, context):
    print('Checking {} at {}...'.format(SITE, event['time']))
    try:
        print (APIKEY)
        req = requests.request("GET", SITE, headers=headers, params=querystring)
        if not validate(str(req.status_code)):
            raise Exception('Validation failed')
    except:
        print('Check failed!')
        raise
    else:
        json_request = req.json()
        delivered = json_request['delivered']
        soft_bounced = json_request['softBounces']
        if percentage(soft_bounced, delivered) > 25:
            raise Exception('Bouncing is higher than 25%')
        else:
            print(percentage(soft_bounced, delivered))
        return event['time']
    finally:
        print('Check complete at {}'.format(str(datetime.now())))