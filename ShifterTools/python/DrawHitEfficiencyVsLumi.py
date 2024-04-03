import sys
import os
import subprocess
import math
from ROOT import TCanvas, TGraph, TGraphAsymmErrors, TFile, TEfficiency
import ctypes
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


def add_points(graph, directory, subdir, layer, usePU):

  ipt=graph.GetN()

  # List runs
  for root, directories, files in os.walk(directory):
    for rundir in sorted(directories):
      if "run_" in rundir:
        # start to process run
        run = rundir[4:]
        #print "processing run ", run
		
        lumi=0
        lumi_err=0

        # Get informations for a given run
        if not os.path.exists(directory+'/'+rundir+'/'+subdir):
          print('  Skipping run', run, '. No subdir ', subdir)
          continue
        filepath = directory+'/'+rundir+'/'+subdir+'/rootfile/SiStripHitEffHistos_run'+run+'.root'
        if not os.path.exists(filepath):
          print('  File', filepath, 'does not exists')
          continue

        frun = TFile(filepath)
        fdir = frun.GetDirectory('SiStripHitEff')        
 
        # for efficiency
        if subdir=='dqm_standard' or subdir=='dqm_withMasking':
          hfound = fdir.Get('goodlayer_found')
          htotal = fdir.Get('goodlayer_total')
        else:
          hfound = fdir.Get('found')
          htotal = fdir.Get('all')

        if htotal == None:
          print('  Missing histogram in file '+frun.GetName())
          continue

        # lumi
        if usePU==0 : hlumi = fdir.Get('instLumi')
        else : hlumi = fdir.Get('PU')
        if hlumi == None:
          print('  Missing lumi/pu histogram in file '+frun.GetName())
          continue
        lumi = hlumi.GetMean()
        lumi_err = hlumi.GetRMS()
        #print "lumi (avg+/-rms): ", lumi, "+/-", lumi_err

        # efficiency for a given layer
        found = hfound.GetBinContent(layer)
        total = htotal.GetBinContent(layer)
        if total>0: eff = found/total
        else: eff = 0
        #print run, eff, lumi, lumi_err

        # remove run without lumi informations
        if lumi>1 :
          eff_vs_lumi.SetPoint(ipt, lumi, eff)
          low = TEfficiency.Bayesian(total, found, .683, 1, 1, False)
          up = TEfficiency.Bayesian(total, found, .683, 1, 1, True);
          if eff-low > 0.01: print('large error bar for run', run, 'layer', layer, 'eff:', '{:.4f}'.format(eff), 'err:', '{:.4f}'.format(eff-low))
          #if lumi_err > lumi/3.: print 'wide lumi range for run', run, 'layer', layer, 'eff:', '{:.4f}'.format(eff), 'lumi/pu:', '{:.4f}'.format(lumi), 'rms:', '{:.4f}'.format(lumi_err)
          eff_vs_lumi.SetPointError(ipt, lumi_err, lumi_err, eff-low, up-eff)
          ipt+=1
        frun.Close()


#------------------------------------------------------------------


if len(sys.argv)<2:
  print("Syntax is:  DrawHitEfficiencyVsLumi.py  ERA [subdir] [usePU] ")
  print("  example:  DrawHitEfficiencyVsLumi.py GR17 [subdir] [1]")
  exit() 

era=str(sys.argv[1])

subdir='withMasking'
if len(sys.argv)>=3: subdir=sys.argv[2]

# option to show results as a function of pu instead of inst. lumi.
usePU=0
if len(sys.argv)>=4: usePU=int(sys.argv[3])


#---------------------


# Produce trend plots for each layer

graphs=[]
c1 = TCanvas()

nlayers = get_nlayers(settings.wwwdir_read+"/"+era, subdir)

# Correct for differences in n bins between dqm and calibtree outputs
if nlayers==21: nlayers=20
if nlayers==23: nlayers=22
if nlayers==31: nlayers=30
if nlayers==35: nlayers=34

print('Found', nlayers, 'layers')

for layer in range(1,nlayers+1):

  print('producing trend plot for layer '+str(layer))

  graphs.append( TGraphAsymmErrors() )
  eff_vs_lumi = graphs[-1]
  xlabels = add_points(eff_vs_lumi, settings.wwwdir_read+"/"+era, subdir, layer, usePU)

  eff_vs_lumi.SetTitle(get_layer_name(layer, nlayers))
  eff_vs_lumi.GetYaxis().SetTitle("hit efficiency")
  if usePU==0 : eff_vs_lumi.GetXaxis().SetTitle("inst. lumi [x10^{30}]")
  else : eff_vs_lumi.GetXaxis().SetTitle("PU")

  eff_vs_lumi.SetMarkerStyle(20)
  eff_vs_lumi.SetMarkerSize(.8)
  eff_vs_lumi.Draw("AP")

  eff_vs_lumi_lastpt = TGraphAsymmErrors()
  npt = eff_vs_lumi.GetN()
  x, y = ROOT.double(0), ROOT.double(0)
  eff_vs_lumi.GetPoint(npt-1, ctypes.c_double(x), ctypes.c_double(y))
  eff_vs_lumi_lastpt.SetPoint(0, x, y)
  eff_vs_lumi_lastpt.SetMarkerStyle(24)
  eff_vs_lumi_lastpt.SetMarkerColor(2)
  eff_vs_lumi_lastpt.Draw("P")

  if usePU==0 : c1.Print("SiStripHitEffTrendPlotVsLumi_layer"+str(layer)+".png")
  else : c1.Print("SiStripHitEffTrendPlotVsPU_layer"+str(layer)+".png")

