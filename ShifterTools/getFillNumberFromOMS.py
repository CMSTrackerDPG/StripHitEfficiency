import sys
from omsapi import OMSAPI

if len(sys.argv)<2:
  print('Error:  Missing argument : ./getBunchesFromOMS.py run_number')
  exit()

run_number = sys.argv[1]

#fill your values
my_app_id='strip_hiteff_monitor'
my_app_secret='409d1eb1-1d42-41ee-9f24-1e1214d19b27'

omsapi = OMSAPI("https://cmsoms.cern.ch/agg/api", "v1", cert_verify=False)
omsapi.auth_oidc(my_app_id,my_app_secret)

# Create a query.
q = omsapi.query("runs")

q.attrs(["run_number", "fill_number", "fill_type_runtime", "stable_beam"])
q.filter("run_number", run_number)

# Execute query & fetch data
response = q.data()

# Display JSON data
print(response.json()['data'][0]['attributes'])

