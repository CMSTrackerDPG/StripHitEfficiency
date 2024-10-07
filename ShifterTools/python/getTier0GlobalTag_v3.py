#!/usr/bin/env python3

import sys
import subprocess
import json
import settings

key_file = cert_file = settings.certificate

def getExpressGT(runnumber):
    out = subprocess.check_output(["curl", "-k", "-s", "--cert", cert_file, "--key", key_file, "https://cmsweb.cern.ch/t0wmadatasvc/prod/express_config?run="+runnumber])
    response = json.loads(out)["result"][0]['global_tag']
    return response

#---------------------------------

if len(sys.argv)<2:
  print('  Missing arguments : '+sys.argv[0]+' runnumber')
  exit()

runnumber = sys.argv[1]

expressGT = getExpressGT(runnumber) 
print(expressGT)
