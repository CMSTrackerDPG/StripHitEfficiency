#!/usr/bin/env python3

import sys
import os
import subprocess
import json

##############################################
def getCerts() -> str:
##############################################
    cert_path = os.getenv('X509_USER_CERT', '')
    key_path = os.getenv('X509_USER_KEY', '')

    certs = ""
    if cert_path:
        certs += f' --cert {cert_path}'
    else:
        print("No certificate, nor proxy provided for Tier0 access")
    if key_path:
        certs += f' --key {key_path}'
    return certs

##############################################
def build_curl_command(url, proxy="", certs="", timeout=30, retries=3, user_agent="MyUserAgent"):
##############################################
    """Builds the curl command with the appropriate proxy, certs, and options."""
    cmd = f'/usr/bin/curl -k -L --user-agent "{user_agent}" '

    if proxy:
        cmd += f'--proxy {proxy} '
    else:
        cmd += f'{certs} '

    cmd += f'--connect-timeout {timeout} --retry {retries} {url}'
    return cmd

##############################################
def getExpressGT(runnumber, proxy="", certs=""):
##############################################
    url = "https://cmsweb.cern.ch/t0wmadatasvc/prod/express_config?run="+str(runnumber)
    cmd = build_curl_command(url, proxy=proxy, certs=certs)
    out = subprocess.check_output(cmd, shell=True)
    response = json.loads(out)["result"][0]['global_tag']
    return response


#---------------------------------------------

if len(sys.argv)<2:
    print('  Missing arguments : '+sys.argv[0]+' runnumber')
    exit()

runnumber = sys.argv[1]

os.environ['X509_USER_KEY'] = os.path.expanduser('~/.globus/userkey.pem')
os.environ['X509_USER_CERT'] = os.path.expanduser('~/.globus/usercert.pem')
certs = getCerts()

expressGT = getExpressGT(runnumber, '', certs=certs)
print(expressGT)

