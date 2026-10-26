#!/bin/bash -f


if [ $# != 1 ]; then
  echo "Usage: $0 fillnumber"
  exit 0;
fi

FILLNUMBER=$1
echo Analyzing fill $FILLNUMBER

# the script guesses that all needed codes are in the current directory
CODEDIR=`pwd`
MODULEDIR=`echo $CODEDIR | awk -FExpertTools '{print $1}' `
#echo $MODULEDIR


# Get list of good runs and corresponding files

# Get list of runs and fill runlist.txt
../getRunsInFill_FromFile.sh $FILLNUMBER > runlist.txt

fullpathfilelist=""
rm -f runshortlist.txt
rm -f filelist.txt

while read RUN DATASET_TYPE DATASET FILL PIX STRIP TRACKING TRIGGERS
do
  if [ "$FILL" == "$1" ]
  then
     echo $RUN $TRACKING
     echo $RUN >> runshortlist.txt
     QUERY="dataset run=$RUN dataset=/StreamExpress/*PromptCalibProdSiStripHitEff-Express*/ALCAPROMPT"
     echo $QUERY
     dataset=`dasgoclient -query="$QUERY"`
     echo "from dataset $dataset"

     QUERY="file dataset=$dataset run=$RUN"
     filelistfull=`dasgoclient -query="$QUERY"`
     #echo $filelistfull > temp.txt

     for FILE in `echo $filelistfull`
     do
       echo $FILE >> filelist.txt
       fullpathfilelist+="'$FILE',"
     done
  fi
done < runlist.txt


# removing last comma
fullpathfilelist=`echo $fullpathfilelist | sed 's/.$//'`
echo "--------------------------"


if [ -f runshortlist.txt ]
  then
    sort runshortlist.txt > runshortlist_ordered.txt
  else
    echo "No corresponding good run found in Collisions ExpressStream"
	exit
fi

FIRSTRUN=`cat runshortlist_ordered.txt | head -1`
NRUNS=`wc -l runshortlist_ordered.txt | awk '{print $1}'`
LASTRUN=`cat runshortlist_ordered.txt | tail -1`
echo $NRUNS runs


# Create a directory for outputs and for work
WORKDIR=Fill_${FILLNUMBER}
if [ -d $WORKDIR -o -d ${WORKDIR}_temp ]
  then
    echo "Directory exists already for this fill. Exiting."
	exit
  else
    mkdir ${WORKDIR}_temp
	cd ${WORKDIR}_temp
fi


# Copy run list and file list in workdir 
cp $CODEDIR/runlist.txt .
cp $CODEDIR/filelist.txt .
NFILES=`cat filelist.txt | wc -l`
echo $NFILES DQM files

globaltag=`$MODULEDIR/ShifterTools/python/getTier0GlobalTag_v3.py $FIRSTRUN`
echo GlobalTag: $globaltag
GLOBALTAG_ERA="Run3"

cmsDriver.py stepHarvest -s ALCAHARVEST:SiStripHitEff --conditions $globaltag --scenario pp --data --era $GLOBALTAG_ERA --filein filetoreplace --no_exec
# trimming comments at beginning of file and inserting file list
sed -n '/import/,$p' stepHarvest_ALCAHARVEST.py > stepHarvest_temp.py
sed -n '1,/filetoreplace/{/filetoreplace/!p}' stepHarvest_temp.py > stepHarvest_ALCAHARVEST_run$FIRSTRUN.py
echo "    fileNames = cms.untracked.vstring(" >> stepHarvest_ALCAHARVEST_run$FIRSTRUN.py
echo "$fullpathfilelist)," >> stepHarvest_ALCAHARVEST_run$FIRSTRUN.py
sed '1,/filetoreplace/d' stepHarvest_temp.py >> stepHarvest_ALCAHARVEST_run$FIRSTRUN.py
rm stepHarvest_temp.py


# Option to output the Summary plot and a tree
outputstring=" Customisation from command line \n\
process.load('Configuration.StandardSequences.Services_cff')\n\
process.TFileService = cms.Service('TFileService',\n\
   fileName = cms.string('GraphAndTree.root')\n\
)\n\
process.alcasiStripHitEfficiencyHarvester.isAtPCL = cms.bool(False)\n"
  outputstring+="process.alcasiStripHitEfficiencyHarvester.doStoreOnTree = cms.untracked.bool(True)\n"

sed -i "s| Customisation from command line|$outputstring|" stepHarvest_ALCAHARVEST_run$FIRSTRUN.py


# Running the job and saving output
#------------------------------------

echo "Starting with Condor ..."
cp  stepHarvest_ALCAHARVEST_run$FIRSTRUN.py stepHarvest_ALCAHARVEST_fill.py

CMSSWDIR=$CMSSW_BASE
#echo $CODEDIR ${WORKDIR}_temp $CMSSWDIR
condor_submit $CODEDIR/job_dqmfiles.sub workdir=$CODEDIR/${WORKDIR}_temp codedir=$CODEDIR cmsswdir=$CMSSWDIR
echo "Results in $WORKDIR"

