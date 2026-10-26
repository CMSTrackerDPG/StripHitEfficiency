import sys
import os
import csv
import json

#inputfilename = 'data/datasets-PromptReco-Collisions23.csv'

narg = len(sys.argv)
if narg < 2:
    print('Syntax: python3',sys.argv[0], 'inputfilename')
    exit()
else:
    inputfilename = sys.argv[1]


outputfilename = 'runs_database_new.txt'
outputfile = open(outputfilename,'w')

nline=0
csvfile = open(inputfilename, newline='')
print('Opening file', inputfilename)
csvreader = csv.reader(csvfile, delimiter=',')
isFirstLine = True
headers=[]
for row in csvreader:
    runinfo={}
    if isFirstLine:
        headers = row
        isFirstLine = False
        print('Column names (for checking):')
        print('run_number' ,':', row[0], ' - ', 'dataset_name' ,':', row[1], ' - ', 'class' ,':', row[2], ' - ', 'tracker-pixel', ':', row[27], ' - ', 'tracker-strip', ':', row[28], ' - ', 'tracker-track', ':', row[29], ' - ', 'oms_attributes', ':', row[30])
    else :

        if len(row)<27 : print('Missing info for run', row[0])

        nline+=1
        pixel_flag = json.loads(row[27])
        strip_flag = json.loads(row[28])
        track_flag = json.loads(row[29])
        oms_attributes = json.loads(row[30])
        if 'fill_number' in oms_attributes:
                runinfo['run_number'] = row[0]
                runinfo['dataset_name'] = row[1]
                runinfo['class'] = row[2]
                runinfo['fill_number'] = oms_attributes['fill_number']
                if 'BAD' not in pixel_flag:
                    runinfo['pixel_flag'] = 'GOOD'
                else :
                    runinfo['pixel_flag'] = 'BAD?'
                if 'BAD' not in strip_flag:
                    runinfo['strip_flag'] = 'GOOD'
                else :
                    runinfo['strip_flag'] = 'BAD?'
                if 'BAD' not in track_flag:
                    runinfo['track_flag'] = 'GOOD'
                else :
                    runinfo['track_flag'] = 'BAD?'
                runinfo['ntriggers'] = oms_attributes['l1_triggers_counter']
                line = runinfo['run_number']+' '+runinfo['class']+' '+runinfo['dataset_name']+' '+str(runinfo['fill_number'])+' '+runinfo['pixel_flag']+' '+runinfo['strip_flag']+' '+runinfo['track_flag']+' '+str(runinfo['ntriggers'])
                #print(line)
                outputfile.write(line+'\n')

outputfile.close()
csvfile.close()

print('Runs info written in', outputfilename)
print(nline, 'entries')
