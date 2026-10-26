#!/bin/sh

DIR=$1

# Cleaning local dir
rm -rf BadModules_*.log
rm -f BadModules_all.log
echo "Removing BadModules_input.txt"
rm -f BadModules_input.txt


## Extracting list of remaining inefficient modules
##   based on jobs logs
i=1
for FILE in `ls $DIR/jobs_output/output*.out` # or error*.err depending on configurations
do
  echo $FILE
  cat $FILE | awk 'BEGIN{doprint=0}{if(match($0,"Detid  	Modules Fibers Apvs")!=0) doprint=1; if(match($0,"total")!=0) doprint=0; if(match($0,"exec.exe")!=0) doprint=0; if(doprint==1) print $0}' > BadModules_$i.log
  cat BadModules_$i.log >> BadModules_all.log
  i=$((i+1))
done
NJOBS=$((i+-1))

## Merging lists of inefficient modules
## (even if tagged in only 1 job)
rm -f merged_file.txt
i=1
if [ -f $DIR/BadModules_input.txt ]
then
  echo "Lines in BadModules_input.txt:" 
  cat $DIR/BadModules_input.txt | awk 'BEGIN{doprint=0}{if(match($0,"Modules Fibers Apvs")!=0) doprint=1; if(doprint==1) print $0}' | wc -l
  python MergeFiles.py $DIR/BadModules_input.txt BadModules_$i.log
  mv merged_file.txt BadModules_input.txt
fi
touch BadModules_input.txt
for FILE in `ls BadModules_*.log`
do
  python3 MergeFiles.py BadModules_input.txt $FILE
  mv -f merged_file.txt BadModules_input.txt
done

echo "Lines in new BadModules_input.txt:" 
wc -l BadModules_input.txt

## Printing summary
echo "Summary of the added inefficient modules from the $NJOBS jobs: (uniq command result)"
sort  BadModules_all.log | grep -v 'Layer' | grep -v 'Disk' | uniq --count
