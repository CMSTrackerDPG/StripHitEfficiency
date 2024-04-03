import sys
import os
import subprocess
import math
from ROOT import TCanvas, TText, TGraphAsymmErrors, TFile, TEfficiency, TLegend
import settings

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptTitle(1)

def get_layer_name(layer, nLayers):
  if layer<5: return 'TIB L'+str(layer)
  if layer>=5 and layer<11: return 'TOB L'+str(layer-4)

  if nLayers==20: # Rings - merged endcap sides
    if layer>=11 and layer<14: return 'TID R'+str(layer-10)
    if layer>=14: return 'TEC R'+str(layer-13)

  if nLayers==22: # Disks - merged endcap sides
    if layer>=11 and layer<14: return 'TID D'+str(layer-10)
    if layer>=14: return 'TEC D'+str(layer-13)

  if nLayers==30: # Rings - separated endcap sides
    if layer>=11 and layer<14: return 'TID- R'+str(layer-10)
    if layer>=14 and layer<17: return 'TID+ R'+str(layer-13)
    if layer>=17 and layer<24: return 'TEC- R'+str(layer-16)
    if layer>=24 and layer<31: return 'TEC+ R'+str(layer-23)

  if nLayers==34: # Disks - separated endcap sides
    if layer>=11 and layer<14: return 'TID- D'+str(layer-10)
    if layer>=14 and layer<17: return 'TID+ D'+str(layer-13)
    if layer>=17 and layer<26: return 'TEC- D'+str(layer-16)
    if layer>=26 and layer<35: return 'TEC+ D'+str(layer-25)

  return ''

def get_short_layer_name(layer, nLayers):
  if layer<5: return 'L'+str(layer)
  if layer>=5 and layer<11: return 'L'+str(layer-4)

  if nLayers==20:
    if layer>=11 and layer<14: return 'R'+str(layer-10)
    if layer>=14 and layer<21: return 'R'+str(layer-13)

  if nLayers==22:
    if layer>=11 and layer<14: return 'D'+str(layer-10)
    if layer>=14 and layer<23: return 'D'+str(layer-13)

  if nLayers==30:
    if layer>=11 and layer<14: return 'R'+str(layer-10)
    if layer>=14 and layer<17: return 'R'+str(layer-13)
    if layer>=17 and layer<24: return 'R'+str(layer-16)
    if layer>=24 and layer<31: return 'R'+str(layer-23)

  if nLayers==34:
    if layer>=11 and layer<14: return 'D'+str(layer-10)
    if layer>=14 and layer<17: return 'D'+str(layer-13)
    if layer>=17 and layer<26: return 'D'+str(layer-16)
    if layer>=26 and layer<35: return 'D'+str(layer-25)

  return ''


def get_nlayers(directory, subdir):
  nlayer = 0
  # Get info from first run
  for root, directories, files in os.walk(directory):
    for rundir in sorted(directories):
      if 'run_' in rundir:
        run = rundir[4:]
        filepath = directory+'/'+rundir+'/'+subdir+'/rootfile/SiStripHitEffHistos_run'+run+'.root'
        if os.path.exists(filepath):

          frun = TFile(filepath)
          fdir = frun.GetDirectory('SiStripHitEff')
          if subdir=='dqm_standard' or subdir=='dqm_withMasking':
            hfound = fdir.Get('goodlayer_found')
            htotal = fdir.Get('goodlayer_total')
          else:
            hfound = fdir.Get('found')
            htotal = fdir.Get('all')

          if htotal != None:
            nlayer = htotal.GetNbinsX()
            return nlayer

  return nlayer


def add_points(graph, directory, subdir, layer):

  ipt=graph.GetN()
  labels = []
 
  # List runs
  for root, directories, files in os.walk(directory):
    for rundir in sorted(directories):
      if 'run_' in rundir:
        # start to process run
        run = rundir[4:]
        #print "processing run ", run
		
        # for efficiency
        if not os.path.exists(directory+'/'+rundir+'/'+subdir):
          print('  Skipping run', run, '. No subdir ', subdir)
          continue
        filepath = directory+'/'+rundir+'/'+subdir+'/rootfile/SiStripHitEffHistos_run'+run+'.root'
        if not os.path.exists(filepath):
          print('  File', filepath, 'does not exists')
          continue

        frun = TFile(filepath)
        fdir = frun.GetDirectory('SiStripHitEff')
        if subdir=='dqm_standard' or subdir=='dqm_withMasking':
          hfound = fdir.Get('goodlayer_found')
          htotal = fdir.Get('goodlayer_total')
        else:
          hfound = fdir.Get('found')
          htotal = fdir.Get('all')

        if htotal == None: 
          print('  Missing histogram in file '+frun.GetName())
          continue

        # efficiency for a given layer
        found = hfound.GetBinContent(int(layer))
        total = htotal.GetBinContent(int(layer))
        if total>0: eff = found/total
        else: eff = 0
        #print run, eff

        graph.SetPoint(ipt, ipt+1, eff)
        labels.append(run)
        low = TEfficiency.Bayesian(total, found, .683, 1, 1, False)
        up = TEfficiency.Bayesian(total, found, .683, 1, 1, True)
        #eff_vs_run.SetPointError(ipt, 0, 0, eff-low, up-eff)
        ipt+=1
        frun.Close()

  axis = graph.GetXaxis()
  for i in range(graph.GetN()) : 
    axis.SetBinLabel(axis.FindBin(i+1), labels[i])
    #print i, axis.FindBin(i+1), labels[i]
  return labels



def draw_subdet(graphs, subdet, nLayers):

  l_min=0
  l_max=0
  subdet_str=''
  
  if subdet==1:
    l_min=1
    l_max=4
    subdet_str='TIB'

  if subdet==2:
    l_min=5
    l_max=9
    subdet_str='TOB'

  if nLayers==20 or nLayers==22:
    if subdet==3:
      l_min=11
      l_max=13
      subdet_str='TID'
    if subdet==5 or subdet==6:
      return

  if nLayers==20:
    if subdet==4:
      l_min=14
      l_max=19
      subdet_str='TEC'

  if nLayers==22:
    if subdet==4:
      l_min=14
      l_max=21
      subdet_str='TEC'

  if nLayers==30 or nLayers==34:
    if subdet==3:
      l_min=11
      l_max=13
      subdet_str='TIDm'
    if subdet==4:
      l_min=14
      l_max=16
      subdet_str='TIDp'

  if nLayers==30:
    if subdet==5:
      l_min=17
      l_max=21
      subdet_str='TECm'
    if subdet==6:
      l_min=23
      l_max=29
      subdet_str='TECp'

  if nLayers==34:
    if subdet==5:
      l_min=17
      l_max=24
      subdet_str='TECm'
    if subdet==6:
      l_min=26
      l_max=33
      subdet_str='TECp'

  leg = TLegend(.92, .3, .99, .7)
  leg.SetHeader('')
  leg.SetBorderSize(0)

  min_y=1.
  for layer in range(l_min,l_max+1):
    if layer==l_min: graphs[layer-1].Draw('AP')
    else: graphs[layer-1].Draw('P')
    graphs[layer-1].SetMarkerColor(1+layer-l_min)
    min_y = graphs[layer-1].GetMinimum() if graphs[layer-1].GetMinimum()<min_y else min_y
    leg.AddEntry(graphs[layer-1], ' '+get_short_layer_name(layer, nLayers), 'p')
  
  graphs[l_min-1].SetTitle(subdet_str)
  haxis = graphs[l_min-1].GetHistogram()
  haxis.GetYaxis().SetRangeUser(min_y, 1.)
  leg.Draw()
  
  c1.Print('SiStripHitEffTrendPlot_Subdet'+str(subdet)+'.png')



#------------------------------------------------------------------


if len(sys.argv)<3:
  print("Syntax is:  DrawHitEfficiencyVsRun.py  ERA  SUBDIRECTORY")
  print("  example:  DrawHitEfficiencyVsRun.py GR17 standard")
  exit() 

era=str(sys.argv[1])
subdir=str(sys.argv[2])


#---------



# Produce trend plots for each layer

graphs=[]

nlayers = get_nlayers(settings.wwwdir_read+"/"+era, subdir)

# Correct for differences in n bins between dqm and calibtree outputs
if nlayers==21: nlayers=20
if nlayers==23: nlayers=22
if nlayers==31: nlayers=30
if nlayers==35: nlayers=34

print('Found', nlayers, 'layers')

for layer in range(1,nlayers):

  print('producing trend plot for layer '+str(layer))

  graphs.append( TGraphAsymmErrors() )
  eff_vs_run = graphs[-1]

  xlabels = add_points(eff_vs_run, settings.wwwdir_read+"/"+era, subdir, layer)

  eff_vs_run.SetTitle(get_layer_name(layer, nlayers))
  #eff_vs_run.GetXaxis().SetTitle("run number")
  eff_vs_run.GetYaxis().SetTitle("hit efficiency")

  c1 = TCanvas()
  eff_vs_run.SetMarkerStyle(20)
  eff_vs_run.SetMarkerSize(.8)
  eff_vs_run.Draw("AP")
  c1.Print("SiStripHitEffTrendPlot_layer"+str(layer)+".png")



# Superimpose graphs for each subdet

for subdet in range(1,7):
  draw_subdet(graphs, subdet, nlayers)


