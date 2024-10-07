# PredictionsModel

Package for predicting hit efficiencies based on the beam filling scheme and some parameters to take into account the HIP effects.
The model is defined in the class **EfficiencyCalculator**.

## For testing:
`python3 test/testEfficiencyCalculator.py ERA  SUBDIRECTORY RUN`

## Fills
OMS is used to get fill number and beam filling scheme with scripts in the *python* directory. To use them the OMS api has to be installed with the following commands:

`git clone https://gitlab.cern.ch/cmsoms/oms-api-client.git  (cern login)`

`cd oms-api-client`

`python3 -m pip install -r requirements.txt`

`python3 setup.py install --user`

