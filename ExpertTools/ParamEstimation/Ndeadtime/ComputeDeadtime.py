import sys
from ROOT import TFile, TH1F, TCanvas, TMath, TLegend, ROOT
import ROOT as R
import ctypes

###
# Code that compute deadtime due to HIP based on
# the coefficient of efficiency variation with pile-up,
# the HIP probability per collision
# and the average pile-up in the data used
# coeff = p_HIP x Nbx_dead_time
# The coefficient (slope) has been measured in an other code
###


### Read arguments

if len(sys.argv)<2:
  print('Syntax is: python3 FILE [PU]')
  exit()

filename=str(sys.argv[1])
run = 'fill'
run += filename.split('/')[-1].split('_fill')[-1].replace('.root','')
directory = filename.replace(filename.split('/')[-1], '')

avg_pu = 0
# get average PU. If not set from argument, will be read from histogram
if len(sys.argv)>=3:
  avg_pu=str(sys.argv[2])


### Get inputs

f = TFile(filename)
d = f.Get('SiStripHitEff')
c = TCanvas()

# PU
#h_PU = d.Get('PU_cutOnTracks') # less biased distribution (not there in old code versions)
h_PU = d.Get('layertotal_vsPU_layer_1') # Give still different PU and better matching
if not h_PU:
    h_PU = d.Get('PU')
if avg_pu==0:
  avg_pu = h_PU.GetMean()
print('PU:', avg_pu)

#--- opening HIP probability per pile-up (Marketa's plot)
ifileHIPprob = TFile("../../inputs/archive/HIPProbPerPU.root")
if not ifileHIPprob:
  print('PUfit.root file not found')
  exit()
c_hipprob = ifileHIPprob.Get('Canvas_1')
h_hipprob = c_hipprob.GetPrimitive('pHIP__1').Clone()
if not h_hipprob:
  print('HIP proba histogram not found')
  exit()
  
#--- opening low pile-up offset
ifileOffset = TFile(directory+'/PUfit_'+run+'.root')
print('Opening file', ifileOffset)
if not ifileOffset:
  print(ifileOffset, ' file not found')
  exit()
h_Offset = ifileOffset.Get('origin')
h_Slope = ifileOffset.Get('slope')
if not h_Offset or not h_Slope:
  print('PU Offset or Slope histogram not found')
  exit()

# Get measured efficiencies
g = d.Get('eff_good')
if not g:
  print('Efficiencies data not found')
  exit()

# Containers preparation
nbins = min(h_hipprob.GetNbinsX(), h_Offset.GetNbinsX())
print('n layers:', nbins)
h_Ineff_meas = TH1F('h_Ineff_meas', '', nbins, 0, nbins)
h_Ineff_fit = TH1F('h_Ineff_fit', '', nbins, 0, nbins)
h_Deadtime = TH1F('h_Deadtime', '', nbins, 0, nbins)
#x = ctypes.c_double(0.0)
#y = ctypes.c_double(0.0)
x = R.double(0.)
y = R.double(0.)
output_file = open('Ndeadtime.txt','w')
print('Results will be written in Ndeadtime.txt')


### Loop over layers

y_values = g.GetY()
print('SUDDET LAYER OFFSET EFF INEFF HIPPROB DEADTIME')
for i in range(1,nbins+1):

    offset = h_Offset.GetBinContent(i)
    offset_err = h_Offset.GetBinError(i)
    slope = h_Slope.GetBinContent(i)
    slope_err = h_Slope.GetBinError(i)
    label = h_Offset.GetXaxis().GetBinLabel(i)
    HIPprob = h_hipprob.GetBinContent(i)
    HIPprob_err = h_hipprob.GetBinError(i)
    label_hip = h_hipprob.GetXaxis().GetBinLabel(i)
    if label_hip != label :
        print('WARNING: inconsistency between layers for offset and HIP proba')
        print(label, '-', label_hip)
        # ordering of layers can be different in endcaps
        for x in range(0,h_hipprob.GetNbinsX()+1):
            label_hip = h_hipprob.GetXaxis().GetBinLabel(x)
            if label_hip == label:
                HIPprob = h_hipprob.GetBinContent(x)
                HIPprob_err = h_hipprob.GetBinError(x)
                print('  Solved. Found layer', label_hip)
    
    # Inefficiency computation from PU dependance (without offset)
    ineff_fit = -1.*slope*0.001*avg_pu
    ineff_fit_err = slope_err*0.001*avg_pu
    h_Ineff_fit.SetBinContent(i, ineff_fit)
    h_Ineff_fit.SetBinError(i, ineff_fit_err)
    h_Ineff_fit.GetXaxis().SetBinLabel(i, label)
    
    # Comparison with global efficiency
    #g.GetPoint(i-1,ctypes.c_double(x), ctypes.c_double(y))
    y = y_values[i-1]
    ineff_meas = offset-y
    h_Ineff_meas.SetBinContent(i, ineff_meas)
    h_Ineff_meas.SetBinError(i, TMath.Sqrt(offset_err*offset_err + g.GetErrorYlow(i-1)*g.GetErrorYlow(i-1)))
    
    # Computation of deadtime
    if HIPprob!=0 and ineff_fit!=0:
        deadtime = -1*slope*0.001/HIPprob/1e-5 # Guillaume's method
        deadtime_err = TMath.Sqrt(slope_err*slope_err/slope/slope + HIPprob_err*HIPprob_err/HIPprob/HIPprob)*deadtime
        print(label, offset, y, ineff_fit, HIPprob, deadtime)
        output_file.write(label+'\t{:.2f}\t{:.2f}\n'.format(deadtime, deadtime_err))
        h_Deadtime.SetBinContent(i, deadtime)
        h_Deadtime.SetBinError(i, deadtime_err)
        h_Deadtime.GetXaxis().SetBinLabel(i, label)
    

### Plotting

c.cd()
# For check
h_Ineff_fit.Draw()
h_Ineff_fit.GetYaxis().SetTitle('Inefficiency')
h_Ineff_fit.SetStats(0)
h_Ineff_meas.SetLineColor(2)
h_Ineff_meas.Draw('same')
leg = TLegend(0.7, .75, .88, .87)
leg.AddEntry(h_Ineff_fit, '-slope x PU', 'LP')
leg.AddEntry(h_Ineff_meas, 'data - offset', 'LP')
leg.SetLineColor(0)
leg.Draw('NDC')
c.Print('Ineff.pdf')

h_Deadtime.Draw()
h_Deadtime.GetYaxis().SetTitle('Dead-time in bx')
h_Deadtime.SetStats(0)
c.Print('Deadtime.pdf')

