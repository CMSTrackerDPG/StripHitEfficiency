import json
from ROOT import TCanvas, TGraph

###
# Code that compute for each layer a weight
# that take into account Ndeadtime and the filling scheme
###

# read dead times:
layer_Ndeadtime = {}
with open('Ndeadtime.txt','r') as fndt:
    lndt=fndt.readlines()
    for l in lndt:
        s=l.split()
        layer = s[0]+' '+s[1]
        nDeadTime = float(s[2])
        error = float(s[3])
        layer_Ndeadtime[layer] = [nDeadTime, error]

#--- opening json files with given fillnumber -> load of the scheme structure
with open('fill.json') as json_input:
    bx_list = json.load(json_input)

c1 = TCanvas()

gDeadtime = {}
ipt=0
file_factors = open('factReweight.txt','w')
for layer in layer_Ndeadtime:
    #compute the hit efficiency with the 'historical' function and compute reweight values corresponding to the filling scheme structure
    NofBx = 0.
    NBxdead = 0.
    NBxdead_max = 0.
    last_train_bx = 0
    nDeadTime = layer_Ndeadtime[layer][0]
    print(layer, nDeadTime)
    gDeadtime[layer] = TGraph()
    ipt=0
    for train in bx_list:
        #print('last_bx', last_train_bx,'train', train[0], '-', train[1])
        index=0
        
        # treat cases where previous train is too close for complete recover
        if last_train_bx!=0 and train[0]-last_train_bx<nDeadTime:
            deadtime = nDeadTime
            for bx in range(last_train_bx+1, train[0]+1):
                deadtime -= 1
                #print('bx', bx, deadtime)
                index=deadtime
                
        # count bx effect
        for bx in range(train[0],train[1]+1):
            NofBx+=1
            NBxdead_max+=nDeadTime
            if float(index) < nDeadTime:
                NBxdead+=index
                #print(index)
                gDeadtime[layer].SetPoint(ipt, bx, index/nDeadTime)
                #print(ipt, bx, index)
                ipt+=1
            if float(index) >= nDeadTime:
                NBxdead+=nDeadTime
                #print(nDeadTime)
                gDeadtime[layer].SetPoint(ipt, bx, 1.)
                #print(ipt, bx, index)
                ipt+=1
            last_train_bx = bx
            index+=1

    print('Nbxtot', NofBx, nDeadTime*NofBx, NBxdead_max)
    factor = NBxdead/NBxdead_max
    error = 0.

    print(layer, NBxdead, NofBx, factor)
    file_factors.write(layer+'\t{:.3f}'.format(factor)+'\t{:.3f}'.format(error)+'\n')
    
gDeadtime['TIB L1'].SetMarkerStyle(20)
gDeadtime['TIB L1'].SetMarkerSize(0.6)
gDeadtime['TIB L1'].SetMarkerColor(4)
gDeadtime['TIB L1'].Draw('AP')
gDeadtime['TIB L1'].GetYaxis().SetTitle('weight')
gDeadtime['TIB L1'].GetXaxis().SetTitle('bx')
gDeadtime['TIB L1'].GetXaxis().SetLimits(330,560)
c1.Print('fill_factor.png')

