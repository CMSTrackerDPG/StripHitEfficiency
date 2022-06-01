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


def fillNumberFromRun_LocalFile(run):
    fill=-1
    localdb = 'fills/runlist_all.txt'
    try:
        f = open(localdb,'r')
    except IOError:
        print('File', localdb, 'not found')
        return fill

    for x in f:
        if x.split(' ')[0]==run:
            fill=x.split(' ')[1]
            return int(fill)
    if fill==-1:
        print('Warning: run', run, 'not found in local db')
    f.close()
    return int(fill)

def fillNumberFromRun_OMS(run):
    # attributes : 'fill_number', 'fill_type_runtime', 'run_number', 'stable_beam' 
    lines = subprocess.check_output(['python3', 'python/getFillNumberFromOMS.py', str(run)])
    output = lines.decode('utf-8').split('\n')[1]
    output = output.replace('\'','\"').replace('True','true').replace('False', 'false')
    output_dict =  json.loads(output)
    if not 'fill_number' in output_dict:
         return -1
    else:
        return int(output_dict['fill_number'])

def get_layer_name(layer, nLayers):
  if layer<5: return 'TIB L'+str(layer)
  if layer>=5 and layer<11: return 'TOB L'+str(layer-4)
  if nLayers==20:
      if layer>=11 and layer<14: return 'TID R'+str(layer-10)
      if layer>=14 and layer<21: return 'TEC R'+str(layer-13)
  if nLayers==22:
      if layer>=11 and layer<14: return 'TID D'+str(layer-10)
      if layer>=14 and layer<23: return 'TEC D'+str(layer-13)
  if nLayers==30:
      if layer>=11 and layer<14: return 'TID R'+str(layer-10)
      if layer>=14 and layer<17: return 'TID R'+str(layer-13)
      if layer>=17 and layer<24: return 'TEC R'+str(layer-16)
      if layer>=24 and layer<31: return 'TEC R'+str(layer-23)
  if nLayers==34:
      if layer>=11 and layer<14: return 'TID D'+str(layer-10)
      if layer>=14 and layer<17: return 'TID D'+str(layer-13)
      if layer>=17 and layer<22: return 'TEC D'+str(layer-16)
      if layer>=26 and layer<35: return 'TEC D'+str(layer-23)
  return ''


#------------------------------------------------------------------



hiteffdir="/afs/cern.ch/cms/tracker/sistrvalidation/WWW/CalibrationValidation/HitEfficiency"

if len(sys.argv)<3:
  print("Syntax is:  DrawHitEfficiencyVsRun.py  ERA  SUBDIRECTORY RUN")
  print("  example:  DrawHitEfficiencyVsRun.py GR18 standard 316202")
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

# PU info
hpu = fdir.Get("PU")
if hpu == None:
	print('  Missing pu histogram in file '+frun.GetName())
	exit()
pu = hpu.GetMean()
pu_err = hpu.GetRMS()
#print( 'PU (avg+/-rms): ', pu, '+/-', pu_err )

# get fill number
filldir='fills/'
fill = fillNumberFromRun_LocalFile(run)
if fill==-1:
    fill = fillNumberFromRun_OMS(run) # contacting OMS can take time
    frunlist = open(filldir+'runlist_all.txt','a+')
    frunlist.write(run+' '+str(fill)+'\n')
    frunlist.close()
if fill==-1:
    print('Fill not found for run', run)
    exit()

# creating json file with fill info if not existing
fillTxt_str = filldir+'fill_'+str(fill)+'.txt'
fillJson_str = filldir+'fill_'+str(fill)+'.json'
if not os.path.isfile(fillJson_str):
    if not os.path.isfile(fillTxt_str):
        print('Requesting beam filling scheme from OMS')
        os.system('python3 python/getBunchesFromOMS.py '+str(fill)+' | tail -1 | sed -e \'s/\'\\\'\'/"/g\' -e \'s/False/false/g\' -e \'s/True/true/g\' -e \'s/None/null/g\' > '+fillTxt_str)
    print('Producing file:', fillJson_str)
    command_str1 = 'python3 python/MakeJson.py '+fillTxt_str
    command_str2 = 'mv fill.json '+fillJson_str
    os.system(command_str1)
    os.system(command_str2)
else:
    print('File', fillJson_str, 'exists')
os.system('cp '+fillJson_str+' fill.json')

# compute expected efficiency

pred = EfficiencyCalculator()
pred.set_pileup(pu)
# get PU distribution
pu_histo = fdir.Get("layerfound_vsPU_layer_"+str(layer))
if pu_histo:
	pred.set_pileup_histo(pu_histo)
pred.set_fillscheme(fillJson_str)
pred.read_inputs("inputs/HIPProbPerPU.root","inputs/LowPUOffset.root")
pred.read_reweight_factors("inputs/factReweight.txt")

##########  

expected = eff
if eff == 0 : expected = 1.

layer_name = get_layer_name(layer, 34)
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

