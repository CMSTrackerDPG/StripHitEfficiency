from ROOT import TFile, TH1D, TCanvas, TMath

###
# Code for transforming HIP probability per ring
# into HIP probability per disk
# based on hit occupancy in endcaps
###

## OPTION
merge_sides = True # True if end-cap disks are merged for both sides
##----------------

# Read HIP probability per pile-up (Marketa's plot)
ifileHIPprob = TFile("../../PredictionsModel/inputs/HIPProbPerPU.root")
c_hipprob = ifileHIPprob.Get("Canvas_1")
h_hipprob = c_hipprob.GetPrimitive("pHIP__1").Clone()

nbins_rings = h_hipprob.GetNbinsX()
print('n layers:', nbins_rings)

prob_per_ring = {}
prob_err_per_ring = {}
for i in range(1,nbins_rings):
    label = h_hipprob.GetXaxis().GetBinLabel(i)
    HIPprob = h_hipprob.GetBinContent(i)
    HIPprob_err = h_hipprob.GetBinError(i)
    prob_per_ring[label] = HIPprob
    prob_err_per_ring[label] = HIPprob_err
print('Proba:')
print(prob_per_ring)
    
# Read occupancy per ring
ifileOcc = open('WheelComposition.txt', 'r')
layers = []
subpart_weight = {}
lines = ifileOcc.readlines()
for line in lines:
    words = line.split(':')
    layer = words[0]
    if layer not in layers : layers.append(layer)
    
    weights = {}
    words = words[1].split()
    nrings = len(words)/2
    for iring in range(0, int(nrings)):
        ring = words[iring*2]
        w_str = words[iring*2+1]
        weight = w_str.split('+/-')[0]
        #print ring, weight
        weights[ring] = float(weight)
    subpart_weight[layer] = weights
#print(subpart_weight)

# Merging end-cap sides weights
subpart_weight_merged = {}
nsides = {}
merged_layers = []
for layer in layers:
    layer_merged = layer[0:-1]
    if layer_merged not in merged_layers:
        merged_layers.append(layer_merged)
        nsides[layer_merged]=1
        subpart_weight_merged[layer_merged]=subpart_weight[layer]
    else:
        nsides[layer_merged]+=1
        for ring in subpart_weight_merged[layer_merged].keys():
            subpart_weight_merged[layer_merged][ring]+=subpart_weight[layer][ring]
#print(subpart_weight_merged)
#print(nsides)
for layer_merged in merged_layers:
    for ring in subpart_weight_merged[layer_merged].keys():
        subpart_weight_merged[layer_merged][ring]/=nsides[layer_merged]
print('Weights:')
print(subpart_weight_merged)



# Reweight HIP prob for disks
#print layers
new_prob = {}
new_prob_err = {}
layers_to_use = []
subpart_weight_to_use = {}
if merge_sides:
    layers_to_use = merged_layers
    subpart_weight_to_use = subpart_weight_merged
else:
    layers_to_use = layers
    subpart_weight_to_use = subpart_weight

print('New proba:')
for layer in layers_to_use:
    subdet = layer.split()[0]
    prob = 0
    prob_err = 0
    for ring in subpart_weight_to_use[layer].keys():
        part = subdet+' '+ring
        if part in prob_per_ring:
            #print layer, ring, prob_per_ring[part], subpart_weight[layer][ring]
            prob += prob_per_ring[part] * subpart_weight_to_use[layer][ring]
            prob_err += prob_err_per_ring[part] * prob_err_per_ring[part] * subpart_weight_to_use[layer][ring] * subpart_weight_to_use[layer][ring] # neglecting error on weights
        else:
            print('WARNING:', part, 'not in list of HIP data')
    prob_err = TMath.Sqrt(prob_err)
    print(layer, '{:.3f}'.format(prob), '+/-', '{:.3f}'.format(prob_err))
    new_prob[ layer ] = prob
    new_prob_err[ layer ] = prob_err


# Saving following input format
ofilename = 'HIPProbPerPU_perDisk.root'
if merge_sides : ofilename = 'HIPProbPerPU_perDisk_mergedSides.root'
ofileHIPprob = TFile(ofilename, 'recreate')

nbin = 10 + len(new_prob)
c = TCanvas('Canvas_1')
h = TH1D('pHIP__1', '', nbin, 0, nbin)
i = 1
# copying barrel data
for ibin in range(1, 11):
    h.SetBinContent(ibin, h_hipprob.GetBinContent(ibin))
    h.SetBinError(ibin, h_hipprob.GetBinError(ibin))
    h.GetXaxis().SetBinLabel(ibin, h_hipprob.GetXaxis().GetBinLabel(ibin))
    i+=1
for layer in sorted(new_prob.keys()):
    h.SetBinContent(i, new_prob[layer])
    h.SetBinError(i, new_prob_err[layer])
    h.GetXaxis().SetBinLabel(i, layer)
    i+=1
h.GetYaxis().SetTitle(h_hipprob.GetYaxis().GetTitle())
h.SetStats(0)
h.Draw('p')
plotname = 'pHIP.pdf'
if merge_sides : plotname = 'pHIP_mergedSides.pdf'
c.Print(plotname)
c.Write()
ofileHIPprob.Close()
