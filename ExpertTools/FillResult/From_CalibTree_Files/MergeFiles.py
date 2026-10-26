import sys

def merge_2files(file1, file2):
    f1 = open(file1, 'r')
    f2 = open(file2, 'r')
    fout = open('merged_file.txt', 'w')

    # Keeping only lines after: (Detid        Modules Fibers Apvs)
    start = False
    lines1 = []
    for line1 in f1.readlines():
        if not start:
            if 'Detid' in line1 and 'Modules Fibers Apvs' in line1:
                start = True
        if start:
            lines1.append(line1)

    start = False
    lines2 = []
    for line2 in f2.readlines():
        if not start:
            if 'Detid' in line2 and 'Modules Fibers Apvs' in line2:
                start = True
        if start:
            lines2.append(line2)


    count=0
    for line1 in lines1:
            if count < len(lines2):
                line2 = lines2[count]
                if line2 == line1:
                    fout.write(line1)
                    #print ('=', line1)
                else:
                    #print ('DIFF',line1,line2)
                    if line2 in lines1: # additionnal module in file1
                        fout.write(line1)
                        #print ('<', line1)
                        count -= 1
                    elif line1 in lines2: # additionnal(s) module in file2
                        #copy all additionnal lines in a row (assumes line1 is in the next file2 lines)
                        while line2 != line1 and count < len(lines2):
                            line2 = lines2[count]                    
                            fout.write(line2)
                            #print ('>', line2)
                            count += 1
                        count -= 1
                    else: # boths line are missing in the other one
                        fout.write(line1)
                        #print ('<', line1)
                        fout.write(line2)
                        #print ('>', line2)
            else:
               fout.write(line1)
            count += 1

#-----------------------------------------------------------------


if len(sys.argv)<3:
  print( "Syntax is: MergeFiles.py FILE1 FILE2")
  exit()

merge_2files(sys.argv[1], sys.argv[2])
