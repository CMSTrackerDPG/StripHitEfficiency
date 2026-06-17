#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data/users/event_display/dpgtkdqm/remotescripts/HitEfficiency2026/CMSSW_16_0_2/src
echo $PWD
eval `scramv1 runtime -sh`
cd /data/users/event_display/dpgtkdqm/remotescripts/HitEfficiency2026/StripHitEfficiency/ShifterTools
sh ./HitEffDriver.sh $1
echo ""
echo "COMPLETED"
echo "Results webpage: https://sistrip-hitefficiency.web.cern.ch/GR26/"
echo "Summary for run $1 --> https://sistrip-hitefficiency.web.cern.ch/GR26/run_$1/shifterSummary/"
