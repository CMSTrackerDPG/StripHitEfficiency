import json
import sys
import os
from ROOT import TFile, TDirectory, TH1F

if len(sys.argv)<2:
  print('Syntax is:', sys.argv[0], ' filename')
  exit() 

file_path = str(sys.argv[1])
if not os.path.isfile(file_path):
    print('File', file_path, 'does not exist')
    exit()
frun = TFile(file_path)
fdir = frun.GetDirectory('SiStripHitEff')

hbx = fdir.Get('bx')
if hbx == None:
    print('Warning: no bx histo')
    exit()

prev_bx = -1
train_start = -1
train_end = -1
bx_list = []
bx_list_compr = []
for i in range(0, hbx.GetNbinsX()):
    content = hbx.GetBinContent(i+1)
    if content>10: # arbitrary threshold larger than 0
        bx_list.append(i)
        if i>prev_bx+1: train_start=i
        prev_bx=i
    else:
        if train_start>-1 and prev_bx>-1:
            train_end=prev_bx
            bx_list_compr.append([train_start, train_end])
            #print(train_start, '-', train_end)
            train_start=-1
print('Fill scheme with', len(bx_list_compr), 'trains,', len(bx_list), 'bx')
#print(bx_list)
#print(bx_list_compr)


fout=open("fill.json","w+")
fout.write(json.dumps(bx_list_compr))
fout.close
