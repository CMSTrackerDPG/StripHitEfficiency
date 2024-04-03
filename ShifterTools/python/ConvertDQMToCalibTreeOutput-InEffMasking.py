import sys
import os
from ROOT import TFile, TH1F, TGraphAsymmErrors, TEfficiency, TTree, gROOT, addressof, TCanvas, TPad, TLegend
from array import array

def GetSubdet(modid):
    #3->6 : TIB, TID, TOB, TEC
    kSubdetOffset = 25
    subdet = (int(modid)>>kSubdetOffset) & 0x7
    return subdet

def GetLayer(modid):
    subdet = GetSubdet(int(modid))
            
    layerStartBit = 14
    layerMask = 0x7

    layer = 0
    # For TIB and TOB
    if subdet==3 or subdet==5:
        layer = ((int(modid)>>layerStartBit) & layerMask)

    return layer
    
def GetRing(modid):
    subdet = GetSubdet(int(modid))

    ringStartBitTID = 9
    ringMaskTID = 0x3
    ringStartBitTEC = 5
    ringMaskTEC = 0x7
    
    ring = 0
    # For TID, returns ring
    if subdet==4:
        ring = ((int(modid)>>ringStartBitTID) & ringMaskTID)
    # For TEC, returns ring
    if subdet==6:
        ring = ((int(modid)>>ringStartBitTEC) & ringMaskTEC)

    return ring

def GetDisk(modid):
    subdet = GetSubdet(int(modid))

    wheelStartBitTID = 11
    wheelMaskTID = 0x3
    wheelStartBitTEC = 14
    wheelMaskTEC = 0xF
    
    wheel = 0
    # For TID, returns ring
    if subdet==4:
        wheel = ((int(modid)>>wheelStartBitTID) & wheelMaskTID)
    # For TEC, returns ring
    if subdet==6:
        wheel = ((int(modid)>>wheelStartBitTEC) & wheelMaskTEC)

    return wheel

def GetSide(modid):

    subdet = GetSubdet(int(modid))
    TIDsideStartBit = 13
    TECsideStartBit = 18
    sideMask = 0x3
    
    side = 0
    # For TID
    if subdet==4:
        side = ((int(modid) >> TIDsideStartBit) & sideMask)
    # For TEC
    if subdet==6: side = ((int(modid) >> TECsideStartBit) & sideMask)

    return side

def GetLabels( nLayers ):
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


def GetILayer(modid, nLayers):
    ilayer = 0
    subdet = GetSubdet(modid)
    subdet_layer = GetLayer(modid)
    subdet_disk = GetDisk(modid)
    side = GetSide(modid)
    if subdet==3 : ilayer = subdet_layer
    if subdet==5 : ilayer = 4 + subdet_layer
    if nLayers==22:
        if subdet==4 : ilayer = 10 + subdet_disk
        if subdet==6 : ilayer = 13 + subdet_disk
    if nLayers==34:
        if subdet==4 : ilayer = 10 + subdet_disk + (side-1)*3
        if subdet==6 : ilayer = 16 + subdet_disk + (side-1)*9

    return ilayer-1


def CreateNHitsHistoFromTree(nhits_array, name, foundhits=True):
    nlay = len(nhits_array)
    hout = TH1F(name, name, nlay, 0, nlay)
    for i in range(nlay):
        if foundhits:
            if nhits_array[i]==0:
                hout.SetBinContent(i+1, 1e-6)
            else:
                hout.SetBinContent(i+1, nhits_array[i])
        else:
            if nhits_array[i]==0:
                hout.SetBinContent(i+1, 1)
            else:
                hout.SetBinContent(i+1, nhits_array[i])
    return hout

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
    
def CloneNHitsHisto( fdir, name, foundhits=True, scale=1. ):
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
                hout.SetBinContent(i, hin.GetBinContent(i)*scale)
        else:
            if hin.GetBinContent(i)==0:
                hout.SetBinContent(i, 1)
            else:
                hout.SetBinContent(i, hin.GetBinContent(i)*scale)
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


def MergeEndCapLayers(hin, nLayers):
    
    nbins = hin.GetNbinsX()
    #hin.Print('all')
    hout = TH1F(hin.GetName()+'_tmp', hin.GetTitle(), nbins-1, 0, nbins-1)
    if nLayers==34:
        hout = TH1F(hin.GetName()+'_mergedSides', hin.GetTitle(), 22, 0, 22)
    if nLayers==30:
        hout = TH1F(hin.GetName()+'_mergedSides', hin.GetTitle(), 20, 0, 20)

    for i in range(10):
        hout.SetBinContent(i, hin.GetBinContent(i))
    if nLayers==34 or nLayers==30:
        for i in range(11):
            hout.SetBinContent(i, hin.GetBinContent(i))
        for i in range(6): # TID
            iside = int(i/3)
            irow = (i-iside*3)%3
            hout.SetBinContent(11+irow, hout.GetBinContent(11+irow)+hin.GetBinContent(11+i))
        if nLayers==34: # TEC endcap disks to be merged
            for i in range(18):
                iside = int(i/9)
                irow = (i-iside*9)%9
                hout.SetBinContent(14+irow, hout.GetBinContent(14+irow)+hin.GetBinContent(17+i))
        if nLayers==30: # TEC endcap disks to be merged
            for i in range(14):
                iside = int(i/7)
                irow = (i-iside*7)%7
                hout.SetBinContent(14+irow, hout.GetBinContent(14+irow)+hin.GetBinContent(17+i))
    else:
        for i in range(11, nbins+1):
            hout.SetBinContent(i, hin.GetBinContent(i))
    #hout.Print('all')
 
    return hout


def DrawSummaryPlot(hfound_clone, htotal_clone, hallfound_clone, halltotal_clone, nLayers, filename='Summary.png', showOnlyGoodModules=False):

    graph_list = []
    
    # For good modules
    # Computing efficiency
    hfound_clone.Sumw2()
    htotal_clone.Sumw2()
    gmeas = TGraphAsymmErrors(nLayers)
    gmeas.SetName('eff_good')
    gmeas.BayesDivide(hfound_clone, htotal_clone)
    gmeas.GetXaxis().SetLimits(0, nLayers)
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
    for k in range(0, nLayers):
        gmeas.SetPointError(k, 0., 0., gmeas.GetErrorYlow(k), gmeas.GetErrorYhigh(k))

    # For all modules
    # Computing efficiency
    hallfound_clone.Sumw2()
    halltotal_clone.Sumw2()
    gmeas2 = TGraphAsymmErrors(nLayers)
    gmeas2.SetName('eff_all')
    gmeas2.BayesDivide(hallfound_clone, halltotal_clone)
    gmeas2.GetXaxis().SetLimits(0, nLayers)
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
    for k in range(1, nLayers+1):
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

    ### Drawing
    c = TCanvas('c'+str(nLayers), '', 10, 10, 800, 600)
    c.SetFillColor(0)
    c.SetGrid()
    gmeas.Draw('AP')
    gmeas.GetXaxis().SetNdivisions(36)

    c.cd()
    overlay = TPad('overlay', '', 0, 0, 1, 1)
    overlay.SetFillStyle(4000)
    overlay.SetFillColor(0)
    overlay.SetFrameFillStyle(4000)
    overlay.Draw('same')
    overlay.cd()
    if not showOnlyGoodModules:
        gmeas2.Draw('AP')
        
    leg = TLegend(0.70, 0.27, 0.88, 0.40)
    leg.AddEntry(gmeas, 'Good Modules', 'p')
    if not showOnlyGoodModules:
        leg.AddEntry(gmeas2, 'All Modules', 'p')
    leg.SetTextSize(0.020)
    leg.SetFillColor(0)
    leg.SetBorderSize(0)
    leg.Draw('same')

    c.SaveAs(filename)
    
    graph_list.append(gmeas)
    graph_list.append(gmeas2)
    return graph_list



def ComputeEfficiency(hfound, htotal, scale=1.):

    geff = TGraphAsymmErrors()
    geff.SetMarkerStyle(20)
    
    found = 0
    total = 0
    sum_bx = 0.
    nbx = 0
    ipt = 0
    firstbx = 0

    for ibx in range(1, htotal.GetNbinsX()):

        if htotal.GetBinContent(ibx) > 1:
            found = hfound.GetBinContent(ibx)
            total = htotal.GetBinContent(ibx)
            eff = found / float(total)
            geff.SetPoint(ipt, ibx, eff*scale)
            low = TEfficiency.Bayesian(total, found, .683, 1, 1, False)
            up = TEfficiency.Bayesian(total, found, .683, 1, 1, True)
            geff.SetPointError(ipt, 0, 0, abs(eff - low), abs(up - eff))
            ipt+=1
                
    return geff
    
    
def ComputeEfficiencyPerTrain(hfound, htotal, scale=1.):

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
                geff_avg.SetPoint(ipt, sum_bx / nbx, eff*scale)
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
        geff_avg.SetPoint(ipt, sum_bx / nbx, eff*scale)
        low = TEfficiency.Bayesian(total, found, .683, 1, 1, False)
        up = TEfficiency.Bayesian(total, found, .683, 1, 1, True)
        geff_avg.SetPointError(ipt, sum_bx / nbx - firstbx, previous_bx - sum_bx / nbx, abs(eff - low), abs(up - eff))
                
    return geff_avg



#------------------------------------------------------------------
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


## Get DQM file
fdqm = TFile(dqm_file)
fdir = fdqm.GetDirectory('DQMData/Run '+run+'/AlCaReco/Run summary/SiStripHitEfficiency')

hfound = fdir.Get('goodlayer_found')
nLayersInDQM = hfound.GetNbinsX()-1
print('nLayersInDQM', nLayersInDQM)


## Get tree
dqm_filename=dqm_file.split('/')[-1]
dqm_dir=dqm_file.replace(dqm_filename, '')
tree_file = dqm_dir+'GraphAndTree_run'+run+'.root'
if not os.path.isfile(tree_file):
    print('File', tree_file, 'does not exist')
    exit()
modEffFile = TFile.Open(tree_file)
tree = modEffFile.Get('pclMetadataWriter/ModEff')


## Compute scale factors : wo/w inefficient modules
# Create with fix length
found_wIneff = [0] * nLayersInDQM
total_wIneff = [0] * nLayersInDQM
found_woIneff = [0] * nLayersInDQM
total_woIneff = [0] * nLayersInDQM
sfactor_found = [0] * nLayersInDQM
sfactor_total = [0] * nLayersInDQM
sfactor_eff = [0] * nLayersInDQM

sf_tree = TTree('scale_factors', 'scale_factors')
# Create a struct
gROOT.ProcessLine(\
                  "struct Entry{\
                  Int_t LAYER;\
                  Float_t SFACTOR;\
                  };")
from ROOT import Entry
sf_entry = Entry()
sf_tree.Branch('LAYER', addressof(sf_entry, 'LAYER'), 'LAYER/I')
sf_tree.Branch('SFACTOR', addressof(sf_entry, 'SFACTOR'), 'SFACTOR/F')

modEff_file = open('ModulesEfficiencies.txt', 'w') 
modIneff_file = open('ModulesInefficiencies.txt', 'w')
layEff_file = open('EfficiencyResults_'+run+'.txt', 'w')

for mod in tree:
    ilayer = GetILayer(mod.DetId, nLayersInDQM)
    #print(mod.Layer, mod.DetId, mod.FoundHits, mod.AllHits, ilayer)
    if ilayer < nLayersInDQM:
        if mod.IsTaggedIneff:
            found_wIneff[ilayer] += mod.FoundHits
            total_wIneff[ilayer] += mod.AllHits
        else:
            found_woIneff[ilayer] += mod.FoundHits
            total_woIneff[ilayer] += mod.AllHits
            found_wIneff[ilayer] += mod.FoundHits
            total_wIneff[ilayer] += mod.AllHits
            if mod.AllHits!=0: 
                modEff_file.write('{:d} {:5g}\n'.format(mod.DetId, mod.FoundHits/float(mod.AllHits))) 
                modIneff_file.write('{:d} {:5g}\n'.format(mod.DetId, 1.-mod.FoundHits/float(mod.AllHits)))
                if mod.FoundHits==0: layEff_file.write('module {:d} efficiency: {:5g} , {:d}/{:d}\n'.format(mod.DetId, mod.FoundHits/float(mod.AllHits), mod.FoundHits, mod.AllHits))
                #module 436233109 efficiency: 0 , 0/20
    else:
        print('ERROR: ilayer out of range')
modEff_file.close()
modIneff_file.close()

eff = 0.
for ilayer in range(nLayersInDQM):
    eff = 0.
    if found_wIneff[ilayer] :
        sfactor_found[ilayer] = found_woIneff[ilayer] / float (found_wIneff[ilayer])
    if total_wIneff[ilayer] :
        sfactor_total[ilayer] = total_woIneff[ilayer] / float (total_wIneff[ilayer])
    if total_woIneff[ilayer] and found_wIneff[ilayer] :
        sfactor_eff[ilayer] = found_woIneff[ilayer] / float(total_woIneff[ilayer]) * total_wIneff[ilayer]  / float (found_wIneff[ilayer])
        eff = found_wIneff[ilayer]/ float (total_wIneff[ilayer])
    else:
        sfactor_eff[ilayer] = 1.
    sf_entry.LAYER = ilayer+1
    sf_entry.SFACTOR = sfactor_eff[ilayer]
    sf_tree.Fill()

    #print( ilayer, sfactor_eff[ilayer])
    #print( ilayer, eff)
#print(sfactor_eff)

## Layer efficiencies containers

# For good modules
hfound_clone = CreateNHitsHistoFromTree(found_woIneff, 'goodlayer_found', True)
htotal_clone = CreateNHitsHistoFromTree(total_woIneff, 'goodlayer_total', False)
#hfound = fdir.Get('EfficiencySummary/found_good')
#hfound_clone = ConvertNHitsHisto(hfound)
#htotal = fdir.Get('EfficiencySummary/all_good')
#htotal_clone = ConvertNHitsHisto(htotal, False)


# For all modules
hallfound = fdir.Get('alllayer_found')
hallfound_clone = ConvertNHitsHisto(hallfound)
halltotal = fdir.Get('alllayer_total')
halltotal_clone = ConvertNHitsHisto(halltotal, False)
#hallfound_clone = CreateNHitsHistoFromTree(found_wIneff, 'alllayer_found', True)
#halltotal_clone = CreateNHitsHistoFromTree(total_wIneff, 'alllayer_total', False)

graphs = DrawSummaryPlot(hfound_clone, htotal_clone, hallfound_clone, halltotal_clone, nLayersInDQM, 'Summary_separatedSides.png')

# Produce summary plots also with endcaps merged
#if nLayersInDQM==34 or nLayersInDQM==30:
hfound_clone_mergedSides = MergeEndCapLayers(hfound_clone, nLayersInDQM)
htotal_clone_mergedSides = MergeEndCapLayers(htotal_clone, nLayersInDQM)
hallfound_clone_mergedSides = MergeEndCapLayers(hallfound_clone, nLayersInDQM)
halltotal_clone_mergedSides = MergeEndCapLayers(halltotal_clone, nLayersInDQM)
nLayers_mergedSides = nLayersInDQM
if nLayersInDQM==34:
    nLayers_mergedSides = 22
if nLayersInDQM==30:
    nLayers_mergedSides = 20
graphs_mergedSides = DrawSummaryPlot(hfound_clone_mergedSides, htotal_clone_mergedSides, hallfound_clone_mergedSides, halltotal_clone_mergedSides, nLayers_mergedSides, 'Summary.png')
#graphs_mergedSides[0].Print('all')


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



## Scales for merged sides

found_wIneff_mergedSides = [0] * neffLayers
total_wIneff_mergedSides = [0] * neffLayers
found_woIneff_mergedSides = [0] * neffLayers
total_woIneff_mergedSides = [0] * neffLayers
sfactor_found_mergedSides = [0] * neffLayers
sfactor_total_mergedSides = [0] * neffLayers
sfactor_eff_mergedSides = [0] * neffLayers

sf_merged_sides_tree = TTree('scale_factors_merged_sides', 'scale_factors_merged_sides')
sf_merged_sides_entry = Entry()
sf_merged_sides_tree.Branch('LAYER', addressof(sf_merged_sides_entry, 'LAYER'), 'LAYER/I')
sf_merged_sides_tree.Branch('SFACTOR', addressof(sf_merged_sides_entry, 'SFACTOR'), 'SFACTOR/F')

if nLayersInDQM==20 or nLayersInDQM==22: # already merged endcap sides
    found_wIneff_mergedSides = found_wIneff
    found_woIneff_mergedSides = found_woIneff
    total_wIneff_mergedSides = total_wIneff
    total_woIneff_mergedSides = total_woIneff
    
if (nLayersInDQM==34 and neffLayers==22) or (nLayersInDQM==30 and neffLayers==20): # endcaps to be merged
    for i in range(10):
        found_wIneff_mergedSides[i] = found_wIneff[i]
        found_woIneff_mergedSides[i] = found_woIneff[i]
        total_wIneff_mergedSides[i] = total_wIneff[i]
        total_woIneff_mergedSides[i] = total_woIneff[i]
    for i in range(6):
        iside = int(i/3)
        irow = (i-iside*3)%3
        found_wIneff_mergedSides[10+irow] += found_wIneff[10+i]
        found_woIneff_mergedSides[10+irow] += found_woIneff[10+i]
        total_wIneff_mergedSides[10+irow] += total_wIneff[10+i]
        total_woIneff_mergedSides[10+irow] += total_woIneff[10+i]
        #print(i, iside, irow, 10+irow)
    
    if nLayersInDQM==34 and neffLayers==22: # endcap disks to be merged
        for i in range(18):
            iside = int(i/9)
            irow = (i-iside*9)%9
            #print(i, iside, irow, 13+irow)
            found_wIneff_mergedSides[13+irow] += found_wIneff[16+i]
            found_woIneff_mergedSides[13+irow] += found_woIneff[16+i]
            total_wIneff_mergedSides[13+irow] += total_wIneff[16+i]
            total_woIneff_mergedSides[13+irow] += total_woIneff[16+i]
    if nLayersInDQM==30 and neffLayers==20: # endcap disks to be merged
        for i in range(14):
            iside = int(i/7)
            irow = (i-iside*7)%7
            #print(i, iside, irow, 13+irow)
            found_wIneff_mergedSides[13+irow] += found_wIneff[16+i]
            found_woIneff_mergedSides[13+irow] += found_woIneff[16+i]
            total_wIneff_mergedSides[13+irow] += total_wIneff[16+i]
            total_woIneff_mergedSides[13+irow] += total_woIneff[16+i]
        
for i in range(neffLayers):
        if found_wIneff_mergedSides[i]:
            sfactor_found_mergedSides[i] = found_woIneff_mergedSides[i]/found_wIneff_mergedSides[i]
        if total_wIneff_mergedSides[i]:
            sfactor_total_mergedSides[i] = total_woIneff_mergedSides[i]/total_wIneff_mergedSides[i]
        if total_woIneff_mergedSides[i] and found_wIneff_mergedSides[i]:
            sfactor_eff_mergedSides[i] = found_woIneff_mergedSides[i]/float(total_woIneff_mergedSides[i]) * total_wIneff_mergedSides[i]/float(found_wIneff_mergedSides[i])
        else:
            sfactor_eff_mergedSides[i] = 1.
        sf_merged_sides_entry.LAYER = i+1
        sf_merged_sides_entry.SFACTOR = sfactor_eff_mergedSides[i]
        sf_merged_sides_tree.Fill()

#print(sfactor_eff_mergedSides)

labels = GetLabels(neffLayers)
eff = 0.
for i in range(neffLayers):
    if total_woIneff_mergedSides[i]!=0:
        eff = found_woIneff_mergedSides[i]/float(total_woIneff_mergedSides[i])
    else: eff=0.
    layEff_file.write('Layer {:d} ({}) has total efficiency {:.6f} {:d}/{:d}\n'.format(i+1, labels[i], eff, found_woIneff_mergedSides[i], total_woIneff_mergedSides[i]))
layEff_file.close()

## VsBx
vsBx_found_histos = []
vsBx_total_histos = []
geff_vsBx = []
geff_avg_vsBx = []
for i in range(1, neffLayers):
    vsBx_found_histos.append(CloneNHitsHisto(fdir, 'VsBx/foundVsBx_layer'+str(i), True))
    vsBx_total_histos.append(CloneNHitsHisto(fdir, 'VsBx/totalVsBx_layer'+str(i), False))
    geff_vsBx.append( ComputeEfficiency(vsBx_found_histos[i-1], vsBx_total_histos[i-1], sfactor_eff_mergedSides[i-1]))
    geff_vsBx[i-1].SetName('effVsBx_layer'+str(i))
    geff_vsBx[i-1].SetTitle('Hit Efficiency vs bx - '+str(labels[i-1]))
    
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
    geff_vsPU.append( ComputeEfficiency( vsPU_found_histos[i-1], vsPU_total_histos[i-1], sfactor_eff_mergedSides[i-1]))
    geff_vsPU[i-1].SetName('effVsPU_layer'+str(i))
    geff_vsPU[i-1].SetTitle('Hit Efficiency vs bx - '+str(labels[i-1]))


## VsLumi
vsLumi_found_histos = []
vsLumi_total_histos = []
geff_vsLumi = []
for i in range(1, neffLayers):
    vsLumi_found_histos.append(CloneNHitsHisto(fdir, 'VsLumi/layerfound_vsLumi_layer_'+str(i)))
    vsLumi_total_histos.append(CloneNHitsHisto(fdir, 'VsLumi/layertotal_vsLumi_layer_'+str(i), False))
    geff_vsLumi.append( ComputeEfficiency(vsLumi_found_histos[i-1], vsLumi_total_histos[i-1], sfactor_eff_mergedSides[i-1]) )
    geff_vsLumi[i-1].SetName('effVsLumi_layer'+str(i))
    geff_vsLumi[i-1].SetTitle('Hit Efficiency vs bx - '+str(labels[i-1]))



## Saving new histos and graphs

out_file = TFile('SiStripHitEffHistos_run'+run+'.root', 'recreate')
out_file.cd()
foutdir = out_file.mkdir('SiStripHitEff')
foutdir.cd()

foutdir.WriteObject(sf_tree, "scale_factors")
foutdir.WriteObject(sf_merged_sides_tree, "scale_factors_merged_sides")

hfound_clone.Write()
htotal_clone.Write()
if len(graphs)>0: graphs[0].Write()
hfound_clone_mergedSides.Write()
htotal_clone_mergedSides.Write()
if len(graphs_mergedSides)>0: graphs_mergedSides[0].Write()

hallfound_clone.Write()
halltotal_clone.Write()
if len(graphs)>1: graphs[1].Write()
hallfound_clone_mergedSides.Write()
halltotal_clone_mergedSides.Write()
if len(graphs_mergedSides)>1: graphs_mergedSides[1].Write()

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

