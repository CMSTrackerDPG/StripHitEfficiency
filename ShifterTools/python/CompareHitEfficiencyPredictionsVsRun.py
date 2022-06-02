import sys
import json
import os
import subprocess
import math
import numpy as np
import ROOT as R
import runregistry
import web_directory

sys.path.append(".")

from EfficiencyCalculator import EfficiencyCalculator

R.gROOT.SetBatch(True)
R.gStyle.SetOptTitle(1)


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

def fillNumberFromRun_RunRegistry(run):
    # Get runs info in querying RunRegistry and filtering
    print('Requesting fill info the Run Registry')
    runinfo = runregistry.get_run( run_number = run )
    if not runinfo:
        return -1
    fill_num = runinfo['oms_attributes']['fill_number']
    return fill_num

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



def add_points(graph, directory, subdir, layer, filter=False):

  ipt=graph.GetN()
  labels = []
 
  # List runs
  for root, directories, files in os.walk(directory):
    for rundir in sorted(directories):
      if "run_" in rundir:
        # start to process run
        run = rundir[4:]
        #print ("processing run ", run)
		
        # for efficiency
        frun = R.TFile(directory+"/"+rundir+"/"+subdir+"/rootfile/SiStripHitEffHistos_run"+run+".root")
        fdir = frun.GetDirectory("SiStripHitEff")
        hfound = fdir.Get("found")
        htotal = fdir.Get("all")

        if htotal == None: 
          print('  Missing histogram in file '+frun.GetName())
          continue

        # measured efficiency for a given layer
        found = hfound.GetBinContent(int(layer))
        if found < 1 : found = 0
        total = htotal.GetBinContent(int(layer))
        if total>0: eff = found/total
        else: eff = 0
        #print (run, eff)
        labels.append(run)
        low = R.TEfficiency.Bayesian(total, found, .683, 1, 1, False)
        up = R.TEfficiency.Bayesian(total, found, .683, 1, 1, True)


        # PU info
        hpu = fdir.Get("PU")
        if hpu == None:
          print('  Missing pu histogram in file '+frun.GetName())
          continue
        pu = hpu.GetMean()
        pu_err = hpu.GetRMS()
        #print( 'PU (avg+/-rms): ', pu, '+/-', pu_err )


        # get fill number
        fill = fillNumberFromRun_LocalFile(run)
        if fill==-1:
          fill = fillNumberFromRun_RunRegistry(run) # contacting RR can take time
          frunlist = open('runlist_all.txt','a+')
          frunlist.write(run+' '+str(fill)+'\n')
          frunlist.close()

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


        # compute expected efficiency

        pred = EfficiencyCalculator()
        # set PU
        #pred.set_pileup(pu)
        pu_histo = fdir.Get("layertotal_vsPU_layer_"+str(layer)) # one entry per expected hits vs PU
        if pu_histo:
            pred.set_pileup_histo(pu_histo)
        pred.set_fillscheme(fillJson_str)
        pred.read_inputs("inputs/HIPProbPerPU.root","inputs/LowPUOffset.root")
        
        ##########  

        expected = eff
        if eff == 0 : expected = 1.
        
        layer_name = get_layer_name(layer)
        pred.read_deadtime("inputs/Ndeadtime.txt",layer_name)

        expected = pred.compute_avg_eff_layer_factorized(layer_name)
        error = np.sqrt(pred.compute_error_avg_eff_layer(layer_name))

        ##########


        # compute ratio and fill graph

        if expected!=0: 
          ratio = eff/expected
        else:
          ratio = 0
        if filter and (ratio>0.998 and ratio<1.002): ratio=0
        graph.SetPoint(ipt, ipt+1, ratio)
        graph.SetPointError(ipt, 0, 0, (eff-low)/expected, (up-eff)/expected)
        if not filter and (ratio <0.998 or ratio >1.002):
            print(run, found, total, '\t{:.4f}'.format(eff), '{:.4f}'.format(expected), '{:.4f}'.format((eff-low)/expected), '\t{:.2f}'.format(pu), '{:.2f}'.format(pu_err))
        #print('ODD', found, total, eff, expected, up)
        ipt+=1
        frun.Close()

  axis = graph.GetXaxis()
  for i in range(graph.GetN()) : 
    axis.SetBinLabel(axis.FindBin(i+1), labels[i])
    #print (i, axis.FindBin(i+1), labels[i])
  return labels



def draw_subdet(graphs, subdet):

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

  if subdet==3:
    l_min=11
    l_max=13
    subdet_str='TIDm'

  if subdet==4:
    l_min=14
    l_max=16
    subdet_str='TIDp'

  if subdet==5:
    l_min=17
    l_max=24
    subdet_str='TECm'

  if subdet==6:
    l_min=26
    l_max=33
    subdet_str='TECp'

  leg = R.TLegend(.92, .3, .99, .7)
  leg.SetHeader('')
  leg.SetBorderSize(0)

  min_y=1.
  for layer in range(l_min,l_max+1):
    if layer==l_min: graphs[layer-1].Draw('AP')
    else: graphs[layer-1].Draw('P')
    graphs[layer-1].SetMarkerColor(1+layer-l_min)
    min_y = graphs[layer-1].GetMinimum() if graphs[layer-1].GetMinimum()<min_y else min_y
    leg.AddEntry(graphs[layer-1], ' '+get_short_layer_name(layer), 'p')
  
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

for layer in range(1,10):#35

  print('producing trend plot for layer '+str(layer))

  graphs.append( R.TGraphAsymmErrors() )
  eff_vs_run = graphs[-1]
  eff_vs_run_filtered = R.TGraphAsymmErrors()

  xlabels = add_points(eff_vs_run, web_repository.wwwdir_read+"/"+era, subdir, layer)
  #add_points(eff_vs_run_filtered, web_repository.wwwdir_read+"/"+era, subdir, layer, True)

  eff_vs_run.SetTitle(get_layer_name(layer))
  #eff_vs_run.GetXaxis().SetTitle("run number")
  eff_vs_run.GetYaxis().SetTitle("Ratio of measured over expected hit efficiency")

  c1 = R.TCanvas()
  eff_vs_run.SetMarkerStyle(20)
  eff_vs_run.SetMarkerSize(.8)

  # if many runs, clean xlabels
  xaxis = eff_vs_run.GetXaxis()
  nbins = len(xlabels)
  nless = int(nbins/40+1)
  #print(nless)
  if nbins > 40 :
    for i in range(eff_vs_run.GetN()) :
      if i%(nless)==0 or i == nbins-1 :
        xaxis.SetBinLabel(xaxis.FindBin(i+1), xlabels[i])
        #print(i, xaxis.FindBin(i+1), xlabels[i])
      else :
        xaxis.SetBinLabel(xaxis.FindBin(i+1), '')
  
  eff_vs_run.Draw("AP")
  l = R.TLine(0, 1, xaxis.GetXmax(), 1)
  l.Draw()

  #eff_vs_run_filtered.SetMarkerStyle(20)
  #eff_vs_run_filtered.SetMarkerSize(.8)
  #eff_vs_run_filtered.SetMarkerColor(2)
  #eff_vs_run_filtered.Draw('P')
  c1.Print("SiStripHitEffTrendPlotVsRun_layer"+str(layer)+".png")



