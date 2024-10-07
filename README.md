# StripHitEfficiency
Tools for shifters and experts for producing hit efficiency results.

## ShifterTools

Directory with the tools for the hit efficiency monitoring to be used by tracker shift leaders.
Comparisons of the measured efficiencies are made with the predicted efficiencies based on the model code from the **PredictionsModel** directory.

### Installation

After having installed the package, few path have to be adapted in some files :
 * `wwwdir` in HitEffDriver.sh and TrendPlots.sh . It is the web repository for storing the outputs.
 * `wwwdir_read` in python/settings.py . It is needed to access stored data and also to store prediction outputs.
 * `certificate` in python/settings.py . This is the grid certificate needed in particular to get the Global Tag of a given run. It is used in python/getTier0GlobalTag_v3.py .

## ExpertTools

Code for producing hit efficiency results of a full LHC fill (several runs).

## PredictionModel

Code to compute predictions of hit efficiency. It is used in the shifter tools for comparison with data.

### Installation

Fill information are retrieved from OMS. This need the api to be installed with the following procedure :

`git clone https://gitlab.cern.ch/cmsoms/oms-api-client.git  (cern login)`

`cd oms-api-client`

`python3 -m pip install -r requirements.txt`

`python3 setup.py install --user` 


