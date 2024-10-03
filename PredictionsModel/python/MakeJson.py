import json
import sys


def ReadJSONFile(name):
    tab=[]
    nwarning=0
    with open(name) as json_file:
        data = json.load(json_file)
        for d in data["data"]:
            if d["attributes"]["intensity_beam_1"] >0.1 and d["attributes"]["intensity_beam_2"] >0.1 :
                if not d["attributes"]["luminosity_detected"]:
                    #print('Warning: 2 beams but no lumi detected for bx', d["attributes"]["bunch_number"])
                    nwarning+=1
                tab.append(d["attributes"]["bunch_number"]+1)

    print(len(tab), 'colliding bunches found')
    if nwarning>0:
        print(nwarning, 'bx with beams but no lumi detected')
    return tab

def PairMakerFromTab(tab):
    begin = tab[0]
    previous = tab[0]
    train=[]
    NewTrain=True
    AtLeastTwoTrains=False
    for i in range(0,len(tab)):
        current=tab[i]
        #if current-previous==1: # in train
            #print('in train', current)
        if current>begin and current-previous>1: # change of train
            end=previous
            #print('end train', end)
            train.append([begin,end])
            begin=current
            #print('new train', current)
            AtLeastTwoTrains=True
        previous = current
        # Special treatment for last bx
        if i==len(tab)-1:
            end=current
            train.append([begin,end])

    return train
    
#################################################################

if len(sys.argv)<2:
  print('Syntax is:', sys.argv[0], ' filename')
  exit() 

tab=ReadJSONFile(str(sys.argv[1]))
#print( tab )
train = PairMakerFromTab(tab)
#print( train )

fout=open("fill_allbx.json","w+")
fout.write(str(tab))
fout.close

fout=open("fill.json","w+")
fout.write(str(train))
fout.close
