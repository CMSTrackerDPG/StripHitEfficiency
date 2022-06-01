import sys
from omsapi import OMSAPI

if len(sys.argv)<2:
  print('Error:  Missing argument : ./getBunchesFromOMS.py fillnumber')
  exit()

fill = sys.argv[1]

#fill your values
my_app_id='strip_hiteff_monitor'
my_app_secret='409d1eb1-1d42-41ee-9f24-1e1214d19b27'

omsapi = OMSAPI("https://cmsoms.cern.ch/agg/api", "v1", cert_verify=False)
omsapi.auth_oidc(my_app_id,my_app_secret)

# Create a query.
#q = omsapi.query("fills")

#q.attrs(["injection_scheme", "bunches_colliding", "fill_number"])
#q.filter("fill_number", 7492)

q = omsapi.query("bunches")
q.filter("fill_number", fill)
q.paginate(page=1, per_page=4000)

# Execute query & fetch data
response = q.data()



# Display JSON data
print(response.json())

