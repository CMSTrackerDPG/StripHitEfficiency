import json
import ctypes
import sys
import os
import subprocess
import math
import numpy as np
from ROOT import TCanvas, TGraph, TGraphErrors, TGraphAsymmErrors, TFile, TEfficiency, TLine, TH1F, TLatex
sys.path.append(".")

from EfficiencyCalculator import EfficiencyCalculator

def fillNumberFromRun_LocalFile(run):
    fill=-1
    localdb = 'runlist_all.txt'
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
    lines = subprocess.check_output(['python3', 'getFillNumberFromOMS.py', str(run)])
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


################################################################################
  
#wwwdir = '/afs/cern.ch/cms/tracker/sistrvalidation/WWW/CalibrationValidation/HitEfficiency/'
wwwdir = '/afs/cern.ch/user/j/jlagram/www/HitEfficiency_11_3_2/'
era = 'GR18'
run = '320674'
fill = -1

if len(sys.argv)<3:
  print('  Missing arguments : CompareWithPredictions.py era runnumber')
  exit()

era = sys.argv[1]
run = sys.argv[2]
 
# get fill number
fill = fillNumberFromRun_LocalFile(run)
if fill==-1:
    fill = fillNumberFromRun_OMS(run) # contacting OMS can take time
    frunlist = open('runlist_all.txt','a+')
    frunlist.write(run+' '+str(fill)+'\n')
    frunlist.close()
if fill==-1:
    print('Fill not found for run', run)
    exit()

print('\nComputation of efficiency for run', run, 'of fill', fill)


### Get informations for a given run

file_path = wwwdir+'run_'+run+'/withMasking/rootfile/SiStripHitEffHistos_run'+run+'.root'
if not os.path.isfile(file_path):
    print('File', file_path, 'does not exist')
    exit()
frun = TFile(file_path)
fdir = frun.GetDirectory('SiStripHitEff')


# efficiency
gmeas = fdir.Get('eff_good')

if gmeas == None:
    print('  Missing graph in file '+frun.GetName())
    exit()

nLayers = gmeas.GetN()-1
tlist = gmeas.GetXaxis().GetLabels()
list_label=[]
for i in range(0, tlist.GetSize()):
    list_label.append(tlist.At(i).GetString().Data())
print('Available layers:')
print(list_label)

if nLayers==22 or nLayers==34:
    print('\nWarning:', nLayers, 'layers found. Prediction computation is only valid per ring for the end-caps and not per disk. Using only barrel layers.' )
    nLayers=10
    # Copying the usable layers
    gmeas_cl = TGraphAsymmErrors(nLayers)
    for i in range(1,nLayers+1):
        y = gmeas.GetPointY(i-1)
        eh = gmeas.GetErrorYhigh(i-1)
        el = gmeas.GetErrorYlow(i-1)
        gmeas_cl.SetPoint(i-1, i-0.5, y)
        gmeas_cl.SetPointEYhigh(i-1,eh)
        gmeas_cl.SetPointEYlow(i-1,el)
    gmeas_cl.GetXaxis().SetLimits(0, nLayers)
    gmeas_cl.SetMarkerColor(2)
    gmeas_cl.SetMarkerSize(1.2)
    gmeas_cl.SetLineColor(2)
    gmeas_cl.SetLineWidth(4)
    gmeas_cl.SetMarkerStyle(20)
    gmeas_cl.SetMinimum(gmeas.GetMinimum())
    gmeas_cl.SetMaximum(gmeas.GetMaximum())
    gmeas_cl.SetTitle(gmeas.GetTitle())
else:
    gmeas_cl = gmeas.Clone()
print('Using', nLayers, 'layers.')


# PU
hpu = fdir.Get('PU')
if hpu == None:
    print('  Missing lumi/pu histogram in file '+frun.GetName())
    exit()
pu = hpu.GetMean()
pu_err = hpu.GetRMS()
print('\nPU from input files:', ' mean={:.3}'.format(pu), ' , rms={:.3}'.format(pu_err))


### Compute Predictions

# creating json file with fill info if not existing
filldir='inputs/fills/'
fillTxt_str = filldir+'fill_'+str(fill)+'.txt'
fillJson_str = filldir+'fill_'+str(fill)+'.json'
if not os.path.isfile(fillJson_str):
    if not os.path.isfile(fillTxt_str):
        print('Requesting beam filling scheme from OMS')
        os.system('python3 getBunchesFromOMS.py '+str(fill)+' | tail -1 | sed -e \'s/\'\\\'\'/"/g\' -e \'s/False/false/g\' -e \'s/True/true/g\' -e \'s/None/null/g\' > '+fillTxt_str)
    print('Producing file:', fillJson_str)
    command_str1 = 'python3 MakeJson.py '+fillTxt_str
    command_str2 = 'mv fill.json '+fillJson_str
    os.system(command_str1)
    os.system(command_str2)
else:
    print('File', fillJson_str, 'exists')
os.system('cp '+fillJson_str+' fill.json')

# setting inputs
pred = EfficiencyCalculator()
pred.set_pileup(pu)
pred.set_fillscheme(fillJson_str)
pred.read_inputs("inputs/HIPProbPerPU.root","inputs/LowPUOffset.root")

# computing predictions
gpred = TGraphErrors()
gpred.SetName('gpred')
print('\nExpected efficiency:')
#######################################
for ilay in range(1, nLayers+1):
    pu_histo = fdir.Get("layertotal_vsPU_layer_"+str(ilay)) # one entry per expected hits vs PU
    if pu_histo:
        pred.set_pileup_histo(pu_histo)
    layer = get_layer_name(ilay,nLayers)
    pred.read_deadtime("inputs/Ndeadtime.txt",layer)
    expected = pred.compute_avg_eff_layer(layer)
    error = np.sqrt(pred.compute_error_avg_eff_layer(layer))
    print('Layer',ilay,layer,': {:.4}'.format(expected),'+/-','{:.3}'.format(error))
    gpred.SetPoint(ilay-1, ilay-0.5, expected) 
    gpred.SetPointError(ilay-1, 0, error) 
    gpred.GetXaxis().SetBinLabel(i, list_label[i-1])
#######################################


frun.Close()
fstore = TFile('SiStripHitEffPredictions_run'+run+'.root', 'recreate')
gpred.Write()

### Draw graphs

c = TCanvas('c1','',1050,750)
c.Divide(1,2)
c.cd(1)
gmeas_cl.SetMinimum(0.98)

# Draw axis
h_axis = TH1F('axis', '', nLayers, 0, nLayers+0.5)
for i in range(1,nLayers+1):
    h_axis.SetBinContent(i,0.99+i*0.001)
    h_axis.GetXaxis().SetBinLabel(i, list_label[i-1])
ymin = gmeas_cl.GetMinimum()
ymax = gmeas_cl.GetMaximum()
h_axis.SetStats(0)
h_axis.GetXaxis().SetLimits(0, nLayers)
h_axis.GetXaxis().LabelsOption("v")
h_axis.GetXaxis().SetLabelSize(0.038)
h_axis.SetMinimum(ymin)
h_axis.SetMaximum(ymax)
h_axis.GetYaxis().SetTitle("Efficiency")
h_axis.Draw('axis')
gmeas_cl.Draw('P')


# Draw vertical lines
lTIB = TLine(4, ymin, 4, ymax)
lTIB.SetLineStyle(3)
lTIB.Draw()
lTOB = TLine(10, ymin, 10, ymax)
lTOB.SetLineStyle(3)
lTOB.Draw()
if nLayers==20 or nLayers==22:
    lTID = TLine(13, ymin, 13, ymax)
else:
    lTID = TLine(16, ymin, 16, ymax)
lTID.SetLineStyle(3)
lTID.Draw()

gpred.SetMarkerStyle(20)
gpred.SetMarkerColor(4)
gpred.Draw('P')

# Draw title
tex1 = TLatex(0.4,0.92,gmeas_cl.GetTitle())
tex1.SetNDC()
tex1.Draw()



# Computing and drawing ratio

c.cd(2)
gmeas2 = gmeas_cl.Clone()
for i in range (1,nLayers+1):
    b1 = gmeas_cl.GetPointY(i-1)
    b2 = gpred.GetPointY(i-1)
    e1 = gmeas_cl.GetErrorY(i-1)
    e2 = gpred.GetErrorY(i-1)
    b1sq = b1*b1
    b2sq = b2*b2
    e1sq = e1*e1
    e2sq = e2*e2
    errsq = (e1sq*b2sq+e2sq*b1sq)
    if b1==0:
        break
    if b2>0:
        gmeas2.SetPoint(i-1,i-0.5,b1/b2)
        gmeas2.SetPointError(i-1,0,0,np.sqrt(errsq),np.sqrt(errsq))
    else:
        gmeas2.SetPoint(i-1,i-0.5,0)
        gmeas2.SetPointError(i-1,0,0,0,0)

ymin=0.995
ymax=1.005
h_axis2 = h_axis.Clone()
h_axis2.SetMinimum(ymin)
h_axis2.SetMaximum(ymax)
h_axis2.GetYaxis().SetTitle('data/prediction')
h_axis2.Draw('axis')

gmeas2.Draw("P")
gmeas2.SetMarkerColor(1)
gmeas2.SetLineColor(1)
gmeas2.SetMinimum(ymin)
gmeas2.SetMaximum(ymax)
l1 = TLine(0,1,nLayers,1)
l1.Draw()
l3=TLine()
l3.SetLineStyle(4)
l3.DrawLine(0,0.998,nLayers,0.998)
l3.DrawLine(0,1.002,nLayers,1.002)
l2 = TLine()
l2.SetLineStyle(3)
l2.DrawLine(4, ymin, 4, ymax)
l2.DrawLine(10, ymin, 10, ymax)
if nLayers==20 or nLayers==22:
    l2.DrawLine(13, ymin, 13, ymax)
else:
    l2.DrawLine(16, ymin, 16, ymax)

c.cd()
c.Print('HitEffPredictions_run'+str(run)+'.png')

c.Write()
fstore.Close()
