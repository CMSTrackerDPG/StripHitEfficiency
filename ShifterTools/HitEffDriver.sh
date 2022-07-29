#!/bin/bash -f

### FUNCTIONS AND VARIABLE DEFINITION
######################################

wwwdir="/afs/cern.ch/cms/tracker/sistrvalidation/WWW/CalibrationValidation/HitEfficiency"

#CreateIndex ()
#{
#    COUNTER=0
#    LASTUPDATE=`date`
#
#    for Plot in `ls *.png`; do
#        if [[ $COUNTER%2 -eq 0 ]]; then
#            cat >> index_new.html  << EOF
#<TR> <TD align=center> <a href="$Plot"><img src="$Plot"hspace=5 vspace=5 border=0 style="width: 90%" ALT="$Plot"></a> 
#  <br> $Plot </TD>
#EOF
#        else
#            cat >> index_new.html  << EOF
#  <TD align=center> <a href="$Plot"><img src="$Plot"hspace=5 vspace=5 border=0 style="width: 90%" ALT="$Plot"></a> 
#  <br> $Plot </TD> </TR> 
#EOF
#        fi
#
#        let COUNTER++
#    done
#
#    cat template/template_index_foot.html | sed -e "s@insertDate@$LASTUPDATE@g" >> index_new.html
#
#    mv -f index_new.html index.html
#}

# Creating html index
CreateIndex ()
{  
    LASTUPDATE=`date`
    
            cat >> index_new.html  << EOF
<TR> <TD align=center> <a href="SiStripHitEffTKMapBad.png"><img src="SiStripHitEffTKMapBad.png"hspace=5 vspace=5 border=0 style="width: 90%" ALT="SiStripHitEffTKMapBad.png"></a> 
  <br> SiStripHitEffTKMapBad.png </TD>
EOF

            cat >> index_new.html  << EOF
  <TD align=center> <a href="SiStripHitEffTKMap.png"><img src="SiStripHitEffTKMap.png"hspace=5 vspace=5 border=0 style="width: 90%" ALT="SiStripHitEffTKMap.png"></a> 
  <br> SiStripHitEffTKMap.png </TD> </TR> 
EOF

            cat >> index_new.html  << EOF
<TR> <TD align=center> <a href="SiStripHitEffTKMapEff.png"><img src="SiStripHitEffTKMapEff.png"hspace=5 vspace=5 border=0 style="width: 90%" ALT="SiStripHitEffTKMapEff.png"></a> 
  <br> SiStripHitEffTKMapEff.png </TD>
EOF

            cat >> index_new.html  << EOF
  <TD align=center> <a href="Summary.png"><img src="Summary.png"hspace=5 vspace=5 border=0 style="width: 90%" ALT="Summary.png"></a> 
  <br> Summary.png </TD> </TR> 
EOF

    cat template/template_index_foot.html | sed -e "s@insertDate@$LASTUPDATE@g" >> index_new.html

    mv -f index_new.html index.html
}


# Storing outputs into www directory
StoreOutputs ()
{

  analysistype=$1
  
  #Now publish all of the relevant files
  #Create the relevant directories on a per run basis
  echo "Creating directories ..."

  #mkdir "/afs/cern.ch/cms/CAF/CMSALCA/ALCA_TRACKERCALIB/SiStrip/CalibrationValidation/HitEfficiency/run_$runnumber"
  mkdir -p "$wwwdir/$ERA/run_$runnumber"
  echo "Creating run_$runnumber/$analysistype"
  mkdir "$wwwdir/$ERA/run_$runnumber/$analysistype"
  mkdir "$wwwdir/$ERA/run_$runnumber/$analysistype/cfg"
  mkdir "$wwwdir/$ERA/run_$runnumber/$analysistype/Plots"
  mkdir "$wwwdir/$ERA/run_$runnumber/$analysistype/sqlite"
  mkdir "$wwwdir/$ERA/run_$runnumber/$analysistype/QualityLog"
  mkdir "$wwwdir/$ERA/run_$runnumber/$analysistype/rootfile"

  echo "Moving output to the proper directory ..."

  #Move the config file
  if [ -f SiStripHitEff_run$runnumber.py ]
  then
    mv SiStripHitEff_run$runnumber.py "$wwwdir/$ERA/run_$runnumber/$analysistype/cfg"
  fi
  if [ -f stepHarvest_ALCAHARVEST_run$runnumber.py ]
  then
    mv stepHarvest_ALCAHARVEST_run$runnumber.py "$wwwdir/$ERA/run_$runnumber/$analysistype/cfg"
  fi

  #Move the log files
  mv "InefficientModules_$runnumber.txt" "$wwwdir/$ERA/run_$runnumber/$analysistype/QualityLog"
  mv "EfficiencyResults_$runnumber.txt" "$wwwdir/$ERA/run_$runnumber/$analysistype/QualityLog"
  if [ -f BadModules_input.txt ]
  then
    mv BadModules_input.txt "$wwwdir/$ERA/run_$runnumber/$analysistype/QualityLog"
  fi
  if [ -f goodPU_filelist.txt ]
  then
    mv goodPU_filelist.txt "$wwwdir/$ERA/run_$runnumber/$analysistype/QualityLog"
  fi
  if [ -f DQM_filelist.txt ]
  then
    mv DQM_filelist.txt "$wwwdir/$ERA/run_$runnumber/$analysistype/QualityLog"
  fi

  #Move the root file containing hot cold maps
  if [ -f SiStripHitEffHistos_run$runnumber.root ]
  then
    mv SiStripHitEffHistos_run$runnumber.root "$wwwdir/$ERA/run_$runnumber/$analysistype/rootfile"
  fi
  if [ -f DQM_V0001_R000${runnumber}__Express__PCLTest__ALCAPROMPT.root ]
  then
    mv DQM_V0001_R000${runnumber}__Express__PCLTest__ALCAPROMPT.root "$wwwdir/$ERA/run_$runnumber/$analysistype/rootfile"
  fi
  if [ -f GraphAndTree_run$runnumber.root ]
  then
    mv GraphAndTree_run$runnumber.root "$wwwdir/$ERA/run_$runnumber/$analysistype/rootfile"
  fi

  #Generate an index.html file to hold the TKMaps
  cat template/template_index_header.html | sed -e "s@insertPageName@Validation Plots --- Hit Efficiency Study --- Tracker Maps@g" > index_new.html
  CreateIndex

  mv index.html "$wwwdir/$ERA/run_$runnumber/$analysistype/Plots"
  mv "SiStripHitEffTKMapBad.png" "$wwwdir/$ERA/run_$runnumber/$analysistype/Plots"
  mv "SiStripHitEffTKMap.png"    "$wwwdir/$ERA/run_$runnumber/$analysistype/Plots"
  mv "SiStripHitEffTKMapEff.png" "$wwwdir/$ERA/run_$runnumber/$analysistype/Plots"
  mv "SiStripHitEffTKMapDen.png" "$wwwdir/$ERA/run_$runnumber/$analysistype/Plots"
  mv "SiStripHitEffTKMapNum.png" "$wwwdir/$ERA/run_$runnumber/$analysistype/Plots"
  mv "Summary.png" "$wwwdir/$ERA/run_$runnumber/$analysistype/Plots/Summary.png"

  # Create the sqlite- and metadata-files
  echo "Preparing the sqlite and metadata files ..."

  if [ -f dbfile.db ]
  then
	ID1=`uuidgen -t`
	#cp dbfile.db SiStripHitEffBadModules@${ID1}.db # before payload whas appended to the file
	mv dbfile.db SiStripHitEffBadModules@${ID1}.db
	cat template/template_SiStripHitEffBadModules.txt | sed -e "s@insertFirstRun@$runnumber@g" -e "s@insertIOV@$runnumber@" > SiStripHitEffBadModules@${ID1}.txt

	mv "SiStripHitEffBadModules@${ID1}.db" "$wwwdir/$ERA/run_$runnumber/$analysistype/sqlite"
	mv "SiStripHitEffBadModules@${ID1}.txt" "$wwwdir/$ERA/run_$runnumber/$analysistype/sqlite"
  fi
  
}


# Storing outputs from predictions computatoins into www directory
StorePredictionsOutputs ()
{

  dirname="predictions"

  #Now publish all of the relevant files
  #Create the relevant directories on a per run basis
  echo "Creating directories ..."

  mkdir -p "$wwwdir/$ERA/run_$runnumber"
  echo "Creating run_$runnumber/$dirname"
  mkdir "$wwwdir/$ERA/run_$runnumber/$dirname"

  echo "Moving output to the proper directory ..."

  #Move files
  mv "predictions_$runnumber.log" "$wwwdir/$ERA/run_$runnumber/$dirname"
  mv "fill.json" "$wwwdir/$ERA/run_$runnumber/$dirname"
  mv "SiStripHitEffPredictions_run$runnumber.root" "$wwwdir/$ERA/run_$runnumber/$dirname"
  mv "HitEffPredictions_run$runnumber.png" "$wwwdir/$ERA/run_$runnumber/$dirname"
}


# Create a page with the most important plots
MakeShifterSummary ()
{

  echo "Creating summary page"
  LASTUPDATE=`date`

  cat template/template_index_header.html | sed -e "s@insertPageName@Validation Plots --- Hit Efficiency Study --- Tracker Maps@g" > index_new.html

  cat >> index_new.html  << EOF
<TR> <TD align=center> <a href="../standard/Plots/SiStripHitEffTKMapBad.png"><img src="../standard/Plots/SiStripHitEffTKMapBad.png"hspace=5 vspace=5 border=0 style="width: 90%" ALT="SiStripHitEffTKMapBad.png"></a> 
  <br> Inefficient modules masked in the other plots</TD>
EOF

  cat >> index_new.html  << EOF
  <TD align=center> <a href="../withMasking/Plots/SiStripHitEffTKMap.png"><img src="../withMasking/Plots/SiStripHitEffTKMap.png"hspace=5 vspace=5 border=0 style="width: 90%" ALT="SiStripHitEffTKMap.png"></a> 
  <br> Remaining inefficient modules </TD> </TR> 
EOF
            
  cat >> index_new.html  << EOF
<TR> <TD align=center> <a href="../withMasking/Plots/SiStripHitEffTKMapEff.png"><img src="../withMasking/Plots/SiStripHitEffTKMapEff.png"hspace=5 vspace=5 border=0 style="width: 90%" ALT="SiStripHitEffTKMapEff.png"></a> 
  <br> Efficiency map </TD>
EOF
            
  cat >> index_new.html  << EOF
  <TD align=center> <a href="../withMasking/Plots/Summary.png"><img src="../withMasking/Plots/Summary.png"hspace=5 vspace=5 border=0 style="width: 90%" ALT="Summary.png"></a> 
  <br> Efficiency per layer </TD> </TR> 
EOF

  cat >> index_new.html  << EOF
<TR> <TD align=center></TD> <TD align=center> <a href="../predictions/HitEffPredictions_run$runnumber.png"><img src="../predictions/HitEffPredictions_run$runnumber.png"hspace=5 vspace=5 border=0 style="width: 90%" ALT="HitEffPredictions_run$runnumber.png"></a> 
  <br> Comparison with predictions </TD> </TR> 
EOF

  cat template/template_index_foot.html | sed -e "s@insertDate@$LASTUPDATE@g" >> index_new.html

  mkdir "$wwwdir/$ERA/run_$runnumber/shifterSummary"
  mv -f index_new.html "$wwwdir/$ERA/run_$runnumber/shifterSummary/index.html"
}




##############################################
### START OF SCRIPT
##############################################


### Options setting
####################

if [ $# -lt 1 ]; then
  echo "Usage: $0 [-n #files] [-e era] runnumber"
  echo "Runs the Hit Efficiency Study"
  exit 0;
fi


# Hard-coded options:
#--------------------
# DQM or Calibtree worklow
#INPUT_TYPE="DQM"
INPUT_TYPE="CALIBTREE"
# Used in DQM workflow:
GLOBALTAG_ERA="Run3"
# Used in Calibtree workflow:
PU_CLEANING=true # REMOVE files with large PU variations. Important due to bias when the cut on the number of tracks is applied during the calibtree production


# Default values for other options
# Run period
ERA="GR22"
# nb of files to be processed for the run
NFILES="4" # Can be "all" in the DQM workflow

# Setting options
while getopts ":n:e:" OPT
do
  #echo $OPT $OPTARG
  case $OPT in
    n)  NFILES="$OPTARG";;
    e)  ERA="$OPTARG";;
    \?) echo "Invalid option -$OPTARG"
  esac
done
shift $((OPTIND-1))

echo "era: $ERA"

# Setting argument
# run number
runnumber=$1
echo "run number: $runnumber"
echo "$NFILES files to be processed,"


### Production of results with the DQM workflow
################################################

if [[ "$INPUT_TYPE" == "DQM" ]]
then

  # Configuration file preparation
  #-------------------------------

  QUERY="dataset run="$runnumber" dataset=/StreamExpress/*PromptCalibProdSiStripHitEff-Express*/ALCAPROMPT"
  dataset=`dasgoclient -query="$QUERY"`
  echo "from dataset $dataset"

  QUERY="file dataset=$dataset run=$runnumber"
  filelistfull=`dasgoclient -query="$QUERY"`

  NTOT=`echo $filelistfull | wc -w`

  if [ "$NFILES" = "all" ]
  then
    NFILES=$NTOT
  fi
  if [ $NFILES -gt $NTOT ]
  then
    NFILES=$NTOT
  fi
  echo "Will run on $NFILES files over the $NTOT available (1 per LS)"

  if [ $NTOT -eq 0 ]
  then
    echo "No file found for run $runnumber"
    exit
  fi


  filelist=`echo $filelistfull | sed -e 's/ /\n/g' | head -$NFILES`
  echo $filelist | sed -e 's/ /\n/g' > DQM_filelist.txt

  echo "--------------------------"
  echo "files that will be used:"
  fullpathfilelist=""
  for file in `echo $filelist`
  do
    fullpathfilelist+="'$file',"
  done

  # removing last comma
  fullpathfilelist=`echo $fullpathfilelist | sed 's/.$//'`
  echo $fullpathfilelist

  echo "--------------------------"


  globaltag=`python/getTier0GlobalTags.py $runnumber`
  echo GlobalTag: $globaltag

  cmsDriver.py stepHarvest -s ALCAHARVEST:SiStripHitEff --conditions $globaltag --scenario pp --data --era $GLOBALTAG_ERA --filein filetoreplace --no_exec
  cp stepHarvest_ALCAHARVEST.py stepHarvest_ALCAHARVEST_run$runnumber.py
  sed -i "s|'filetoreplace'|$fullpathfilelist|g" stepHarvest_ALCAHARVEST_run$runnumber.py

  # Option to output the Summary plot and a tree
  outputstring=" Customisation from command line \n\
process.load('Configuration.StandardSequences.Services_cff')\n\
process.TFileService = cms.Service('TFileService',\n\
   fileName = cms.string('GraphAndTree.root')\n\
)\n\
process.alcasiStripHitEfficiencyHarvester.isAtPCL = cms.bool(False)\n"
  outputstring+="process.alcasiStripHitEfficiencyHarvester.doStoreOnTree = cms.untracked.bool(True)\n"

  sed -i "s| Customisation from command line|$outputstring|" stepHarvest_ALCAHARVEST_run$runnumber.py


  # Running the job and saving outputs
  #------------------------------------

  echo "Launching cmsRun ..."
  cmsRun stepHarvest_ALCAHARVEST_run$runnumber.py >& "run_${runnumber}_dqm.log"
  touch run_${runnumber}_dqm.log

  cat run_${runnumber}_dqm.log | awk 'BEGIN{doprint=0}{if(match($0,"Global Info")!=0) doprint=1; if(match($0,"modules")!=0) doprint=0; if(match($0,"DQMFileSaver::globalEndRun")!=0) {doprint=0;} if(match($0,"MessageLogger")!=0) {doprint=0;} if(doprint==1) print $0}' > InefficientModules_$runnumber.txt
  cat run_${runnumber}_dqm.log | awk 'BEGIN{doprint=0}{if(match($0,"occupancy")!=0) doprint=1; if(match($0,"efficiency")!=0) doprint=1; if(match($0,"modules")!=0) doprint=1; if(match($0,"%MSG")!=0) {doprint=0;} if(match($0,"tempfilename")!=0) {doprint=0;} if(match($0,"Global Info")!=0) {doprint=0;} if(match($0,"DQMFileSaver::globalEndRun")!=0) {doprint=0;} if(match($0,"MessageLogger")!=0) {doprint=0;} if(doprint==1) print $0}' > EfficiencyResults_$runnumber.txt

  mv SiStripHitEffTKMapBad_NEW.png SiStripHitEffTKMapBad.png 
  mv SiStripHitEffTKMap_NEW.png SiStripHitEffTKMap.png
  mv SiStripHitEffTKMapEff_NEW.png SiStripHitEffTKMapEff.png
  mv SiStripHitEffTKMapDen_NEW.png SiStripHitEffTKMapDen.png
  mv SiStripHitEffTKMapNum_NEW.png SiStripHitEffTKMapNum.png
  rm BadModules_NEW.log
  mv promptCalibConditions.db dbfile.db
  rm Summary.root
  mv GraphAndTree.root GraphAndTree_run$runnumber.root 
  
  #dqm_output_file=`ls -rt | grep DQM_V00 | grep ${runnumber} | grep __ALCAPROMPT.root | tail -1`
  #echo $dqm_output_file " produced"
  echo "Output format conversion ..."
  python3 python/ConvertDQMToCalibTreeOutput.py DQM_V0001_R000${runnumber}__Express__PCLTest__ALCAPROMPT.root

  StoreOutputs dqm
fi
# end of dqm workflow



### Production of results with the CalibTree workflow
######################################################

if [[ "$INPUT_TYPE" == "CALIBTREE" ]]
then

  # Listing inputs
  #----------------

  EOSpath="/store/group/dpg_tracker_strip/comm_tracker/Strip/Calibration/calibrationtree"
  echo "from directory: $EOSpath/$ERA"

  # get the first files of that run
  filelist=`eos ls $EOSpath/$ERA | grep $runnumber | sort -t '_' -k 3n | head -$NFILES`
  filelistfull=`eos ls $EOSpath/$ERA | grep $runnumber`

  NTOT=`echo $filelistfull | wc -w`
  if [ $NFILES -gt $NTOT ]
  then
    NFILES=$NTOT
  fi
  echo "Will run on $NFILES files over the $NTOT available"

  if [ $NTOT -eq 0 ]
  then
    echo "No file found in $EOSpath/$ERA for run $runnumber"
    exit
  fi

  echo $filelist > filelist.txt
  goodfilelist=$filelist

  echo "--------------------------"



  # Checking PU in files
  #----------------------

  if $PU_CLEANING
  then

    IFILE=1
    PUfilelist=""
    rm -f SiStripHitEffHistos_run${runnumber}_*.root
    for file in `echo $filelist`
    do

      FILEID=`echo $file | awk -F'_' '{print $3} '| sed -e 's/.root//'`
      if [[ "$FILEID" == "" ]]
      then
        FILEID="0"
      fi
      echo "RUNNING ON FILE $FILEID: $file"
      fullpathfile="'root://eoscms//eos/cms$EOSpath/$ERA/$file'"

      cp template/SiStripHitEff_template.py "SiStripHitEff_run$runnumber.py"
      sed -i "s/newrun/$runnumber/g" "SiStripHitEff_run$runnumber.py"
      sed -i "s|'root://eoscms//eos/cms/newfilelocation'|$fullpathfile|g" "SiStripHitEff_run$runnumber.py"

      rm -f BadModules_input.txt

      cmsRun "SiStripHitEff_run$runnumber.py" >& "run_${runnumber}_$FILEID.log"
      rm run_${runnumber}_$FILEID.log
      mv "SiStripHitEffHistos_run$runnumber.root" "SiStripHitEffHistos_run${runnumber}_$FILEID.root"
      PUfilelist+="SiStripHitEffHistos_run${runnumber}_$FILEID.root,"

      IFILE=$((IFILE+1))
    done


    # Analyzing the PU info in the output files
    #echo $PUfilelist
    echo "Analysing PU conditions ..."
    echo ""
    rm -f goodPU_filelist.txt
    python3 python/analyse_files_PU.py $PUfilelist >& "run_${runnumber}_PU.log"
    cat run_${runnumber}_PU.log
    PUfilelist_toremove=`echo $PUfilelist | sed -e 's/,/ /g' `
    rm -f $PUfilelist_toremove

    # Cleaned list of files
    if [ -f goodPU_filelist.txt ]
    then
      goodfilelist=`cat goodPU_filelist.txt`
    else
      echo "Missing file 'goodPU_filelist.txt'"
      exit
    fi

    NGOOD=`echo $goodfilelist | wc -w`
    if [ $NGOOD -eq 0 ]
    then
     echo "No calibTree file with stable PU conditions for run $runnumber"
     exit
    fi

  fi
  # end of PU cleaning


  echo "files that will be used:"
  fullpathfilelist=""
  for file in `echo $goodfilelist`
  do
    FILEID=`echo $file | awk -F'_' '{print $3} '| sed -e 's/.root//'`
    if [[ "$FILEID" == "0" ]]
    then
      fullpathfilelist+="'root://eoscms//eos/cms$EOSpath/$ERA/calibTree_$runnumber.root',"
    else
      fullpathfilelist+="'root://eoscms//eos/cms$EOSpath/$ERA/calibTree_${runnumber}_$FILEID.root',"
    fi
  done
  fullpathfilelist=`echo $fullpathfilelist | sed 's/.$//'`
  echo $fullpathfilelist

  echo "--------------------------"




  # Lauching production
  #---------------------

  ### Running first pass for identifying inefficient modules

  cp template/SiStripHitEff_template.py "SiStripHitEff_run$runnumber.py"
  sed -i "s/newrun/$runnumber/g" "SiStripHitEff_run$runnumber.py"
  sed -i "s|'root://eoscms//eos/cms/newfilelocation'|$fullpathfilelist|g" "SiStripHitEff_run$runnumber.py"

  echo "Launching cmsRun ..."

  cmsRun "SiStripHitEff_run$runnumber.py" >& "run_$runnumber.log" 

  cat run_$runnumber.log | awk 'BEGIN{doprint=0}{if(match($0,"New IOV")!=0) doprint=1;if(match($0,"%MSG")!=0) {doprint=0;} if(match($0,"Message")!=0) {doprint=0;} if(doprint==1) print $0}' > InefficientModules_$runnumber.txt
  cat run_$runnumber.log | awk 'BEGIN{doprint=0}{if(match($0,"occupancy")!=0) doprint=1;if(match($0,"efficiency")!=0) doprint=1; if(match($0,"%MSG")!=0) {doprint=0;} if(match($0,"tempfilename")!=0) {doprint=0;} if(match($0,"New IOV")!=0) {doprint=0;} if(match($0,"generation")!=0) {doprint=0;} if(doprint==1) print $0}' > EfficiencyResults_$runnumber.txt

  mv run_$runnumber.log run_${runnumber}_standard.log

  # Storing outputs in www directory
  StoreOutputs standard



  ### Running the analysis a second time in masking some inefficient modules

  mv BadModules.log BadModules_input.txt

  cp template/SiStripHitEff_template.py "SiStripHitEff_run$runnumber.py"
  sed -i "s/newrun/$runnumber/g" "SiStripHitEff_run$runnumber.py"
  sed -i "s|'root://eoscms//eos/cms/newfilelocation'|$fullpathfilelist|g" "SiStripHitEff_run$runnumber.py"

  echo "Launching cmsRun for second job ..."

  cmsRun "SiStripHitEff_run$runnumber.py" >& "run_$runnumber.log" 

  # don't want to save this one where the inefficient modules have been masked and can not be identified
  rm dbfile.db

  cat run_$runnumber.log | awk 'BEGIN{doprint=0}{if(match($0,"New IOV")!=0) doprint=1;if(match($0,"%MSG")!=0) {doprint=0;} if(match($0,"Message")!=0) {doprint=0;} if(doprint==1) print $0}' > InefficientModules_$runnumber.txt
  cat run_$runnumber.log | awk 'BEGIN{doprint=0}{if(match($0,"occupancy")!=0) doprint=1;if(match($0,"efficiency")!=0) doprint=1; if(match($0,"%MSG")!=0) {doprint=0;} if(match($0,"tempfilename")!=0) {doprint=0;} if(match($0,"New IOV")!=0) {doprint=0;} if(match($0,"generation")!=0) {doprint=0;} if(doprint==1) print $0}' > EfficiencyResults_$runnumber.txt

  mv run_$runnumber.log run_${runnumber}_withMasking.log

  StoreOutputs withMasking

  rm BadModules.log
  #rm -f SiStripHitEffHistos_run${runnumber}_*.root

fi
# end of calibtree workflow



### Comparison with Predictions
################################

echo "Computing predicted efficiencies ..."
python3 python/CompareWithPredictions.py $ERA $runnumber $INPUT_TYPE >& "predictions_$runnumber.log"
StorePredictionsOutputs 
MakeShifterSummary

### produce and store trend plots
##################################
./TrendPlots.sh $ERA


echo "Done."
