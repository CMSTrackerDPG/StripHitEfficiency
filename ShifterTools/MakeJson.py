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
                tab.append(d["attributes"]["bunch_number"])

    print(len(tab), 'colliding bunches found')
    if nwarning>0:
        print(nwarning, 'bx with beams but no lumi detected')
    return tab

def PairMakerFromTab(tab):
    train=[]
    NewTrain=True
    AtLeastTwoTrains=False
    for i in range(0,len(tab)):
        if NewTrain==False:
            if tab[i]==current+1:
                current=tab[i]
            else:
                end=current
                NewTrain=True
                if AtLeastTwoTrains:
                    train.append([begin,end+1])
                else:
                    train.append([begin+1,end+1])
                AtLeastTwoTrains=True
        else:
            begin=tab[i]
            current=begin
            NewTrain=False
        if i==len(tab)-1:
            end=tab[i]
            if AtLeastTwoTrains:
                train.append([begin,end+1])
            else:
                train.append([begin+1,end+1])

    return train
    
#################################################################

if len(sys.argv)<2:
  print('Syntax is:', sys.argv[0], ' filename')
  exit() 

tab=ReadJSONFile(str(sys.argv[1]))
#print( tab )
train = PairMakerFromTab(tab)
#print( train )
train_string=str(train)
#print( train_string )
fout=open("fill.json","w+")
fout.write(train_string)
fout.close
