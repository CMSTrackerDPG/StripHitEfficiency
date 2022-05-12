import sys
import json
import os
import subprocess
import math
import numpy as np
import ROOT as R

sys.path.append(".")

from EfficiencyCalculator import EfficiencyCalculator

R.gROOT.SetBatch(True)
R.gStyle.SetOptTitle(1)


def fillNumberFromRun(run):
    f = open("/afs/cern.ch/user/j/jlagram/work/public/HitEfficiency/Fills/GR18/runlist_all.txt","r")
    fill=-1
    for x in f:
        if x.split(' ')[0]==run:
            fill=x.split(' ')[1]
            return int(fill)
    if fill==-1:
        print('Warning: no fill found for run', run)
    return int(fill)

def get_layer_name(layer):
  if layer<5: return 'TIB L'+str(layer)
  if layer>=5 and layer<11: return 'TOB L'+str(layer-4)
  if layer>=11 and layer<14: return 'TID- D'+str(layer-10)
  if layer>=14 and layer<17: return 'TID+ D'+str(layer-13)
  if layer>=17 and layer<26: return 'TEC- W'+str(layer-16)
  if layer>=26 and layer<35: return 'TEC+ W'+str(layer-25)
  return ''

def get_short_layer_name(layer):
  if layer<5: return 'L'+str(layer)
  if layer>=5 and layer<11: return 'L'+str(layer-4)
  if layer>=11 and layer<14: return 'D'+str(layer-10)
  if layer>=14 and layer<17: return 'D'+str(layer-13)
  if layer>=17 and layer<26: return 'W'+str(layer-16)
  if layer>=26 and layer<35: return 'W'+str(layer-25)
  return ''





#------------------------------------------------------------------



hiteffdir="/afs/cern.ch/cms/tracker/sistrvalidation/WWW/CalibrationValidation/HitEfficiency"

if len(sys.argv)<3:
  print("Syntax is:  DrawHitEfficiencyVsRun.py  ERA  SUBDIRECTORY")
  print("  example:  DrawHitEfficiencyVsRun.py GR17 standard")
  exit() 

era=str(sys.argv[1])
subdir=str(sys.argv[2])
run=str(sys.argv[3])
rundir="run_"+run
layer = 1

#---------


print('Arguments are:  run', run, '  layer', layer)

frun = R.TFile(hiteffdir+"/"+era+"/"+rundir+"/"+subdir+"/rootfile/SiStripHitEffHistos_run"+run+".root")
fdir = frun.GetDirectory("SiStripHitEff")
hfound = fdir.Get("found")
htotal = fdir.Get("all")

if htotal == None:
	print('  Missing histogram in file '+frun.GetName())
	exit()

# measured efficiency for a given layer
found = hfound.GetBinContent(int(layer))
if found < 1 : found = 0
total = htotal.GetBinContent(int(layer))
if total>0: eff = found/total
else: eff = 0
#print (run, eff)
low = R.TEfficiency.Bayesian(total, found, .683, 1, 1, False)
up = R.TEfficiency.Bayesian(total, found, .683, 1, 1, True)

fill = fillNumberFromRun(run)

# PU info
hpu = fdir.Get("PU")
if hpu == None:
	print('  Missing pu histogram in file '+frun.GetName())
	exit()
pu = hpu.GetMean()
pu_err = hpu.GetRMS()
#print( 'PU (avg+/-rms): ', pu, '+/-', pu_err )

# creating json file with fill info if not existing
filldir='/afs/cern.ch/user/j/jlagram/work/public/HitEfficiency/Fills/GR18/'
fillJson_str = 'inputs/fills/fill'+str(fill)+'.json'
if not os.path.isfile(fillJson_str):
	if not os.path.isfile(filldir+'fill_'+str(fill)+'.txt'):
		## TODO: Change lines by getting fill info from OMS
		print('  Missing fill info for fill '+str(fill)+' in '+filldir)
		exit()
	else:
		print('Producing file:', fillJson_str)
		fillTxt_str = filldir+'fill_'+str(fill)+'.txt'
		command_str1 = 'python3 MakeJson.py '+fillTxt_str
		command_str2 = 'mv fill.json '+fillJson_str
		os.system(command_str1)
		os.system(command_str2)


# compute expected efficiency

pred = EfficiencyCalculator()
pred.set_pileup(pu)
pred.set_fillscheme(fillJson_str)
pred.read_inputs("inputs/HIPProbPerPU.root","inputs/LowPUOffset.root")

##########  

expected = eff
if eff == 0 : expected = 1.

layer_name = get_layer_name(layer)
pred.read_deadtime("inputs/Ndeadtime.txt",layer_name)

expected = pred.compute_avg_eff_layer(layer_name)
expected2 = pred.compute_avg_eff_layer_factorized(layer_name)
error = np.sqrt(pred.compute_error_avg_eff_layer(layer_name))

print('Expected:', expected, expected2)

##########


# compute ratio and fill graph

if expected!=0:
	ratio = eff/expected
else:
	ratio = 0
print('RUN  FOUND  TOTAL  \tEFF  EXPECTED  REL_ERR  PU  PU_ERR')
print(run, found, total, '\t{:.4f}'.format(eff), '{:.4f}'.format(expected), '{:.4f}'.format((eff-low)/expected), '\t{:.2f}'.format(pu), '{:.2f}'.format(pu_err))

frun.Close()

