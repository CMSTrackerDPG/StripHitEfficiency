if [ "$1" = "" ] 
then
    echo " Syntax : script.sh fill_temp_directory"
    exit
fi

WORKDIR=`pwd`
MODULEDIR=`echo $CODEDIR | awk -FExpertTools '{print $1}' `

DIR=$1
FILLNUMBER=`echo $DIR | sed -e 's/Fill_//' -e 's/_temp//'`
RUNNUMBER=`ls $DIR/stepHarvest_ALCAHARVEST_run*.py | awk -F/ '{print $NF}'  | sed -e 's/stepHarvest_ALCAHARVEST_run//' -e 's/.py//'`

echo "Processing directory $DIR"
echo "Fill : $FILLNUMBER"
echo "First run : $RUNNUMBER"
cp -r $DIR ${DIR}_new
cd  ${DIR}_new

OUTPUT=`ls jobs_output/*.err`
echo "Log file : $OUTPUT"
cp $OUTPUT fill_${FILLNUMBER}_dqm.log

echo "Saving summaries ..."
cat fill_${FILLNUMBER}_dqm.log | awk 'BEGIN{doprint=0}{if(match($0,"Global Info")!=0) doprint=1; if(match($0,"modules")!=0) doprint=0; if(match($0,"DQMFileSaver::globalEndRun")!=0) {doprint=0;} if(match($0,"MessageLogger")!=0) {doprint=0;} if(doprint==1) print $0}' > InefficientModules_fill${FILLNUMBER}.txt
cat fill_${FILLNUMBER}_dqm.log | awk 'BEGIN{doprint=0}{if(match($0,"occupancy")!=0) doprint=1; if(match($0,"efficiency")!=0) doprint=1; if(match($0,"modules")!=0) doprint=1; if(match($0,"%MSG")!=0) {doprint=0;} if(match($0,"tempfilename")!=0) {doprint=0;} if(match($0,"Global Info")!=0) {doprint=0;} if(match($0,"DQMFileSaver::globalEndRun")!=0) {doprint=0;} if(match($0,"MessageLogger")!=0) {doprint=0;} if(doprint==1) print $0}' > EfficiencyResults_fill${FILLNUMBER}.txt

echo "Renaming files ..."
mv SiStripHitEffTKMapBad_NEW.png SiStripHitEffTKMapBad.png 
rm SiStripHitEffTKMapBad_NEW.root
mv SiStripHitEffTKMap_NEW.png SiStripHitEffTKMap.png
rm SiStripHitEffTKMap_NEW.root
mv SiStripHitEffTKMapEff_NEW.png SiStripHitEffTKMapEff.png
rm SiStripHitEffTKMapEff_NEW.root
mv SiStripHitEffTKMapDen_NEW.png SiStripHitEffTKMapDen.png
rm SiStripHitEffTKMapDen_NEW.root
mv SiStripHitEffTKMapNum_NEW.png SiStripHitEffTKMapNum.png
rm SiStripHitEffTKMapNum_NEW.root
rm BadModules_NEW.log
rm promptCalibConditions.db
rm -f *.cc
rm Summary.root


echo ""
echo "Output format conversion ..."
DQM_OUTPUT=`ls DQM_V0001_R000*__Express__PCLTest__ALCAPROMPT.root`
mv GraphAndTree.root GraphAndTree_run$RUNNUMBER.root
python3 $MODULEDIR/ShifterTools/python/ConvertDQMToCalibTreeOutput.py $DQM_OUTPUT
cat  EfficiencyResults_fill${FILLNUMBER}.txt | grep module | grep -v modules | grep -v Number | grep Layer | awk '{print $6}' > bad_detids.txt

mkdir dqm_standard
mv *.png dqm_standard
mv InefficientModules_fill${FILLNUMBER}.txt dqm_standard
mv EfficiencyResults_fill${FILLNUMBER}.txt dqm_standard

# Creating same results with inefficient modules masked
python3 $MODULEDIR/ShifterTools/python/ConvertDQMToCalibTreeOutput-InEffMasking.py $DQM_OUTPUT
print_TrackerMap InefficientModules_fill_${FILLNUMBER}.txt "Inefficient Modules" SiStripHitEffTKMapBad.png
print_TrackerMap ModulesInefficiencies.txt "Detector Inefficiency" SiStripHitEffTKMap.png 4500 False False 0. 1.
print_TrackerMap ModulesEfficiencies.txt "SiStrip Hit Efficiency Map" SiStripHitEffTKMapEff.png 4500 False False 0.9 1.0
rm ModulesInefficiencies.txt
rm ModulesEfficiencies.txt

mkdir dqm_withMasking
mv *.png dqm_withMasking
mv SiStripHitEffTKMap*.root dqm_withMasking 
mv EfficiencyResults_${RUNNUMBER}.txt dqm_withMasking 
mv SiStripHitEffHistos_run${RUNNUMBER}.root dqm_withMasking

# Creating results with a stronger masking
echo
python3 $MODULEDIR/ShifterTools/python/ConvertDQMToCalibTreeOutput-InEffMasking.py $DQM_OUTPUT bad_detids.txt
print_TrackerMap InefficientModules_fill_${FILLNUMBER}.txt "Inefficient Modules" SiStripHitEffTKMapBad.png
print_TrackerMap ModulesInefficiencies.txt "Detector Inefficiency" SiStripHitEffTKMap.png 4500 False False 0. 1.
print_TrackerMap ModulesEfficiencies.txt "SiStrip Hit Efficiency Map" SiStripHitEffTKMapEff.png 4500 False False 0.9 1.0
rm ModulesInefficiencies.txt
rm ModulesEfficiencies.txt

mkdir dqm_withStrongMasking
mv *.png dqm_withStrongMasking
mv SiStripHitEffTKMap*.root dqm_withStrongMasking
mv EfficiencyResults_${RUNNUMBER}.txt dqm_withStrongMasking
mv SiStripHitEffHistos_run${RUNNUMBER}.root dqm_withStrongMasking
mv bad_detids.txt dqm_withStrongMasking

echo "Cleaning ..."
rm stepHarvest_ALCAHARVEST_fill.py
rm stepHarvest_ALCAHARVEST_fill_temp.py
rm -rf jobs_output
cd ..
mv ${DIR}_new Fill_$FILLNUMBER
