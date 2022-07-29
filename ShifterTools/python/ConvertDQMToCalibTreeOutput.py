import sys
import os
from ROOT import TFile, TH1F, TGraphAsymmErrors, TEfficiency

def ConvertNHitsHisto( hin, foundhits=True ):
    # Clone in shifting by 1 bin:
    nbins = hin.GetNbinsX()
    hout = TH1F(hin.GetName(), hin.GetTitle(), nbins-1, 0, nbins-1)
    for i in range(2,nbins+1):
        if foundhits:
            if hin.GetBinContent(i)==0:
                hout.SetBinContent(i-1, 1e-6)
            else:
                hout.SetBinContent(i-1, hin.GetBinContent(i))
        else:
            if hin.GetBinContent(i)==0:
                hout.SetBinContent(i-1, 1)
            else:
                hout.SetBinContent(i-1, hin.GetBinContent(i))
    return hout


def CloneNHitsHisto( fdir, name, foundhits=True ):
    hin = fdir.Get(name)
    if hin == None:
        print('Histo not found:', name)
        return None
    
    hout = hin.Clone()
    
    nbins = hout.GetNbinsX()
    #print('Histo', name, 'Nbins:', nbins)
    for i in range(0,nbins+1):
        if foundhits:
            if hin.GetBinContent(i)==0:
                hout.SetBinContent(i, 1e-6)
            else:
                hout.SetBinContent(i, hin.GetBinContent(i))
        else:
            if hin.GetBinContent(i)==0:
                hout.SetBinContent(i, 1)
            else:
                hout.SetBinContent(i, hin.GetBinContent(i))
    hout.Sumw2()
    
    return hout


def CloneHisto( fdir, name ):
    hin = fdir.Get(name)
    if hin == None:
        print('Histo not found:', name)
        return None
    else:
        hout = hin.Clone()
        return hout


def GetLabels( nlayers ):
    # 34 -> wheels & sides
    # 30 -> rings & sides
    # 22 -> wheels
    # 20 -> rings
    if nLayers==34:
        return ['TIB L1', 'TIB L2', 'TIB L3', 'TIB L4', 'TOB L1', 'TOB L2', 'TOB L3', 'TOB L4', 'TOB L5', 'TOB L6', 'TID- D1', 'TID- D2', 'TID- D3', 'TID+ D1', 'TID+ D2', 'TID+ D3', 'TEC- D1', 'TEC- D2', 'TEC- D3', 'TEC- D4', 'TEC- D5', 'TEC- D6', 'TEC- D7', 'TEC- D8', 'TEC- D9', 'TEC+ D1', 'TEC+ D2', 'TEC+ D3', 'TEC+ D4', 'TEC+ D5', 'TEC+ D6', 'TEC+ D7', 'TEC+ D8', 'TEC+ D9']
    if nLayers==30:
        return ['TIB L1', 'TIB L2', 'TIB L3', 'TIB L4', 'TOB L1', 'TOB L2', 'TOB L3', 'TOB L4', 'TOB L5', 'TOB L6', 'TID- R1', 'TID- R2', 'TID- R3', 'TID+ R1', 'TID+ R2', 'TID+ R3', 'TEC- R1', 'TEC- R2', 'TEC- R3', 'TEC- R4', 'TEC- R5', 'TEC- R6', 'TEC- R7', 'TEC+ R1', 'TEC+ R2', 'TEC+ R3', 'TEC+ R4', 'TEC+ R5', 'TEC+ R6', 'TEC+ R7']
    if nLayers==22:
        return ['TIB L1', 'TIB L2', 'TIB L3', 'TIB L4', 'TOB L1', 'TOB L2', 'TOB L3', 'TOB L4', 'TOB L5', 'TOB L6', 'TID D1', 'TID D2', 'TID D3', 'TEC D1', 'TEC D2', 'TEC D3', 'TEC D4', 'TEC D5', 'TEC D6', 'TEC D7', 'TEC D8', 'TEC D9']
    if nLayers==20:
        return ['TIB L1', 'TIB L2', 'TIB L3', 'TIB L4', 'TOB L1', 'TOB L2', 'TOB L3', 'TOB L4', 'TOB L5', 'TOB L6', 'TID R1', 'TID R2', 'TID R3', 'TEC R1', 'TEC R2', 'TEC R3', 'TEC R4', 'TEC R5', 'TEC R6', 'TEC R7']
    return []


def ComputeEfficiencyPerTrain(hfound, htotal):

    spaceBetweenTrains = 25
    geff_avg = TGraphAsymmErrors()
    geff_avg.SetMarkerStyle(20)
    
    previous_bx = -9999;
    delta_bx = 0;
    found = 0
    total = 0
    sum_bx = 0.
    nbx = 0
    ipt = 0
    firstbx = 0

    for ibx in range(1, htotal.GetNbinsX()):

        if htotal.GetBinContent(ibx) > 1:
            delta_bx = ibx - previous_bx
            if delta_bx > spaceBetweenTrains and nbx > 0 and total > 0:
                #print(ibx, htotal.GetBinContent(ibx), delta_bx, spaceBetweenTrains, nbx, total)
                eff = found / float(total)
                geff_avg.SetPoint(ipt, sum_bx / nbx, eff)
                low = TEfficiency.Bayesian(total, found, .683, 1, 1, False)
                up = TEfficiency.Bayesian(total, found, .683, 1, 1, True)
                geff_avg.SetPointError(ipt, sum_bx / nbx - firstbx, previous_bx - sum_bx / nbx, eff - low, up - eff)
                ipt+=1
                found = 0
                total = 0
                sum_bx = 0
                nbx = 0
                firstbx = ibx
            sum_bx += ibx
            found += hfound.GetBinContent(ibx)
            total += htotal.GetBinContent(ibx)
            nbx += 1
            
            previous_bx = ibx
        
    # last train
    if total > 0:
        eff = found / float(total)
        geff_avg.SetPoint(ipt, sum_bx / nbx, eff)
        low = TEfficiency.Bayesian(total, found, .683, 1, 1, False)
        up = TEfficiency.Bayesian(total, found, .683, 1, 1, True)
        geff_avg.SetPointError(ipt, sum_bx / nbx - firstbx, previous_bx - sum_bx / nbx, eff - low, up - eff)
                
    return geff_avg



#------------------------------------------------------------------


if len(sys.argv)<2:
    print('Missing file name argument')
    exit()

dqm_file = sys.argv[1]

if not os.path.isfile(dqm_file):
    print('File', dqm_file, 'does not exist')
    exit()

run=''
words = dqm_file.split('_')
for word in words:
    if 'R000' in word:
        run = word.replace('R000', '')
print('Run:', run)


fdqm = TFile(dqm_file)
fdir = fdqm.GetDirectory('DQMData/Run '+run+'/AlCaReco/Run summary/SiStripHitEfficiency')



## Layer efficiencies

# For good modules
hfound = fdir.Get('goodlayer_found')
hfound_clone = ConvertNHitsHisto(hfound)
htotal = fdir.Get('goodlayer_total')
htotal_clone = ConvertNHitsHisto(htotal, False)

# Computing efficiency
hfound_clone.Sumw2()
htotal_clone.Sumw2()
nbins = hfound_clone.GetNbinsX()
gmeas = TGraphAsymmErrors(nbins-1)
gmeas.SetName('eff_good')
gmeas.BayesDivide(hfound_clone, htotal_clone)
gmeas.SetMarkerColor(2)
gmeas.SetMarkerSize(1.2)
gmeas.SetLineColor(2)
gmeas.SetLineWidth(4)
gmeas.SetMarkerStyle(20)
gmeas.SetMinimum(0.9)
gmeas.SetMaximum(1.001)
gmeas.GetYaxis().SetTitle('Efficiency')
gmeas.SetTitle('Hit Efficiency - run '+run)
gmeas.GetXaxis().SetNdivisions(36)
nLayers = gmeas.GetN()
print('N layers:', nLayers)
for k in range(0, nLayers):
    gmeas.SetPointError(k, 0., 0., gmeas.GetErrorYlow(k), gmeas.GetErrorYhigh(k))

# For all modules
hallfound = fdir.Get('alllayer_found')
hallfound_clone = ConvertNHitsHisto(hallfound)
halltotal = fdir.Get('alllayer_total')
halltotal_clone = ConvertNHitsHisto(halltotal, False)

# Computing efficiency
hallfound_clone.Sumw2()
halltotal_clone.Sumw2()
nbins = hallfound_clone.GetNbinsX()
gmeas2 = TGraphAsymmErrors(nbins-1)
gmeas2.SetName('eff_all')
gmeas2.BayesDivide(hfound_clone, htotal_clone)
gmeas2.SetMarkerColor(1)
gmeas2.SetMarkerSize(1.2)
gmeas2.SetLineColor(1)
gmeas2.SetLineWidth(4)
gmeas2.SetMarkerStyle(21)
gmeas2.SetMinimum(0.9)
gmeas2.SetMaximum(1.001)
gmeas2.GetYaxis().SetTitle('Efficiency')
gmeas2.SetTitle('Hit Efficiency - run '+run)
gmeas2.GetXaxis().SetNdivisions(36)
for k in range(0, nLayers):
    gmeas2.SetPointError(k, 0., 0., gmeas.GetErrorYlow(k), gmeas.GetErrorYhigh(k))

# Labels
labels = GetLabels(nLayers)
for k in range(1, nLayers):
    if nLayers==34:
        gmeas.GetXaxis().SetBinLabel(int(((k + 1) * 100 + 2) / (nLayers)-4), labels[k-1])
        gmeas2.GetXaxis().SetBinLabel(int(((k + 1) * 100 + 2) / (nLayers)-4), labels[k-1])
    if nLayers==22:
        gmeas.GetXaxis().SetBinLabel(int((k + 1) * 100 / (nLayers)-6), labels[k-1])
        gmeas2.GetXaxis().SetBinLabel(int((k + 1) * 100 / (nLayers)-6), labels[k-1])
    if nLayers==30:
        gmeas.GetXaxis().SetBinLabel(int((k + 1) * 100 / (nLayers)-4), labels[k-1])
        gmeas2.GetXaxis().SetBinLabel(int((k + 1) * 100 / (nLayers)-4), labels[k-1])
    if nLayers==20:
        gmeas.GetXaxis().SetBinLabel(int((k + 1) * 100 / (nLayers)-7), labels[k-1])
        gmeas2.GetXaxis().SetBinLabel(int((k + 1) * 100 / (nLayers)-7), labels[k-1])



## Modules efficiencies per layer

neffLayers = 0
eff_histos = []
for obj in fdir.GetListOfKeys():
    name = obj.GetName()
    if 'eff_layer' in name:
        eff_histos.append(CloneHisto(fdir, name))
        neffLayers+=1
print(neffLayers, 'Layers found for modules efficiencies')


## EventInfo

hPU = CloneHisto(fdir, 'EventInfo/PU')
hbx = CloneHisto(fdir, 'EventInfo/bx')
hlumi = CloneHisto(fdir, 'EventInfo/instLumi')
# To add: profile n tracks vs PU
hntracks = CloneHisto(fdir, 'EventInfo/ntracks')


## HotAndCold maps

TH2D_histos = []
f2Ddir = fdir.GetDirectory('MissingHits')
if f2Ddir == None:
    print('Directory HotAndCold maps not found, skipping 2D histos')
else:
    for obj in f2Ddir.GetListOfKeys():
        TH2D_histos.append( CloneHisto(f2Ddir, obj.GetName()) )
    

## Resolutions

resol_histos = []
for i in range(1, neffLayers):
    resol_histos.append( CloneHisto(fdir, 'Resolutions/resol_layer_'+str(i)) )


## VsBx
vsBx_found_histos = []
vsBx_total_histos = []
geff_vsBx = []
geff_avg_vsBx = []
for i in range(1, neffLayers):
    vsBx_found_histos.append(CloneNHitsHisto(fdir, 'VsBx/foundVsBx_layer'+str(i)))
    vsBx_total_histos.append(CloneNHitsHisto(fdir, 'VsBx/totalVsBx_layer'+str(i), False))
    geff_vsBx.append( TGraphAsymmErrors() )
    geff_vsBx[i-1].SetName('effVsBx_layer'+str(i))
    geff_vsBx[i-1].SetTitle('Hit Efficiency vs bx - '+str(labels[i-1]))
    geff_vsBx[i-1].BayesDivide(vsBx_found_histos[i-1], vsBx_total_histos[i-1])
    geff_vsBx[i-1].SetMarkerStyle(20)
    
    ## Avg over trains
    geff_avg_vsBx.append( ComputeEfficiencyPerTrain(vsBx_found_histos[i-1], vsBx_total_histos[i-1]) )
    geff_avg_vsBx[i-1].SetName('effVsBxAvg_layer'+str(i))
    geff_avg_vsBx[i-1].SetTitle('Hit Efficiency vs bx - '+str(labels[i-1]))


## VsPU
vsPU_found_histos = []
vsPU_total_histos = []
geff_vsPU = []
for i in range(1, neffLayers):
    vsPU_found_histos.append(CloneNHitsHisto(fdir, 'VsPu/layerfound_vsPU_layer_'+str(i)))
    vsPU_total_histos.append(CloneNHitsHisto(fdir, 'VsPu/layertotal_vsPU_layer_'+str(i), False))
    geff_vsPU.append( TGraphAsymmErrors() )
    geff_vsPU[i-1].SetName('effVsPU_layer'+str(i))
    geff_vsPU[i-1].SetTitle('Hit Efficiency vs bx - '+str(labels[i-1]))
    geff_vsPU[i-1].BayesDivide(vsPU_found_histos[i-1], vsPU_total_histos[i-1])
    geff_vsPU[i-1].SetMarkerStyle(20)


## VsLumi
vsLumi_found_histos = []
vsLumi_total_histos = []
geff_vsLumi = []
for i in range(1, neffLayers):
    vsLumi_found_histos.append(CloneNHitsHisto(fdir, 'VsLumi/layerfound_vsLumi_layer_'+str(i)))
    vsLumi_total_histos.append(CloneNHitsHisto(fdir, 'VsLumi/layertotal_vsLumi_layer_'+str(i), False))
    geff_vsLumi.append( TGraphAsymmErrors() )
    geff_vsLumi[i-1].SetName('effVsLumi_layer'+str(i))
    geff_vsLumi[i-1].SetTitle('Hit Efficiency vs bx - '+str(labels[i-1]))
    geff_vsLumi[i-1].BayesDivide(vsLumi_found_histos[i-1], vsLumi_total_histos[i-1])
    geff_vsLumi[i-1].SetMarkerStyle(20)



## Saving new histos and graphs

out_file = TFile('SiStripHitEffHistos_run'+run+'.root', 'recreate')
out_file.cd()
foutdir = out_file.mkdir('SiStripHitEff')
foutdir.cd()

hfound_clone.Write()
htotal_clone.Write()
gmeas.Write()

hallfound_clone.Write()
halltotal_clone.Write()
gmeas2.Write()

for h in eff_histos:
    h.Write()

hPU.Write()
hbx.Write()
hlumi.Write()
hntracks.Write()

for histo2D in TH2D_histos:
    histo2D.Write()

for i in range(0, neffLayers-1):
    resol_histos[i].Write()
    vsBx_found_histos[i].Write()
    vsBx_total_histos[i].Write()
    geff_vsBx[i].Write()
    geff_avg_vsBx[i].Write()
    vsPU_found_histos[i].Write()
    vsPU_total_histos[i].Write()
    geff_vsPU[i].Write()
    vsLumi_found_histos[i].Write()
    vsLumi_total_histos[i].Write()
    geff_vsLumi[i].Write()

out_file.Close()
fdqm.Close()
