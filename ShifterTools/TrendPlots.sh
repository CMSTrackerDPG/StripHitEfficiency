#!/bin/bash -f


wwwdir="/afs/cern.ch/cms/tracker/sistrvalidation/WWW/CalibrationValidation/HitEfficiency"

CreateTrendPlotsIndex()
{
  rootname=$1
  LASTUPDATE=`date`

  #Generate an index.html file to hold the plots
  cat template/template_index_header.html | sed -e "s@insertPageName@Hit Efficiency Trend Plots@g" > index_new.html

  if [ "$rootname" = "SiStripHitEffTrendPlot" ]
  then
    for subdet in {1..6}
    do
      if [ "$(($subdet%2))" -eq 1 ]; then echo "<TR>" >> index_new.html; fi
      cat >> index_new.html  << EOF
<TD align=center> <a href="${rootname}_Subdet${subdet}.png"><img src="${rootname}_Subdet${subdet}.png"hspace=5 vspace=5 border=0 style="width: 90%" ALT="${rootname}_Subdet${subdet}.png"></a> 
  <br> ${rootname}_Subdet${subdet}.png </TD>
EOF
      if [ "$(($subdet%2))" -eq 0 ]; then echo "</TR>" >> index_new.html; fi
     done
  fi

  for layer in {1..34}
  do
    if [ "$(($layer%2))" -eq 1 ]; then echo "<TR>" >> index_new.html; fi
    cat >> index_new.html  << EOF
<TD align=center> <a href="${rootname}_layer${layer}.png"><img src="${rootname}_layer${layer}.png"hspace=5 vspace=5 border=0 style="width: 90%" ALT="${rootname}_layer${layer}.png"></a> 
  <br> ${rootname}_layer${layer}.png </TD>
EOF
    if [ "$(($layer%2))" -eq 0 ]; then echo "</TR>" >> index_new.html; fi
   done

  cat template/template_index_foot.html | sed -e "s@insertDate@$LASTUPDATE@g" >> index_new.html
   
}


StoreTrendPlotsOutput()
{

  rootname=$1
  era=$2
  subdir=$3

  if [ "$rootname" = "SiStripHitEffTrendPlot" ]
  then
    for subdet in {1..6}
    do
       mv ${rootname}_Subdet${subdet}.png $wwwdir/$era/TrendPlots/$subdir/
    done
  fi

  for layer in {1..34}
  do
     mv ${rootname}_layer${layer}.png $wwwdir/$era/TrendPlots/$subdir/
  done

  # create index
  CreateTrendPlotsIndex $rootname

  mv index_new.html $wwwdir/$era/TrendPlots/$subdir/index.html

}


#---------------------------------------------

ERA=$1
echo "Era: $ERA"

INPUT_TYPE="CALIBTREE"
DIR=""
if [[ "$2" != "" ]]
then
  INPUT_TYPE=$2
fi
if [[ "$INPUT_TYPE" == "DQM" ]]
then
  DIR="dqm_"
fi

echo "Input type: $INPUT_TYPE"
echo "Associated directory: $DIR"

#----------------------------------------------

mkdir -p $wwwdir/$ERA/TrendPlots

# produce and store trend plots

echo "Using outputs from '${DIR}standard' directories"
mkdir -p $wwwdir/$ERA/TrendPlots/${DIR}standard
python3 python/DrawHitEfficiencyVsRun.py $ERA ${DIR}standard
StoreTrendPlotsOutput SiStripHitEffTrendPlot $ERA ${DIR}standard

echo "Using outputs from '${DIR}withMasking' directories"
mkdir -p $wwwdir/$ERA/TrendPlots/${DIR}withMasking
python3 python/DrawHitEfficiencyVsRun.py $ERA ${DIR}withMasking
StoreTrendPlotsOutput SiStripHitEffTrendPlot $ERA ${DIR}withMasking

echo "Using outputs from '${DIR}withMasking' directories for results vs inst. lumi."
mkdir -p $wwwdir/$ERA/TrendPlots/vsLumi
python3 python/DrawHitEfficiencyVsLumi.py $ERA ${DIR}withMasking
StoreTrendPlotsOutput SiStripHitEffTrendPlotVsLumi $ERA vsLumi

echo "Using outputs from '${DIR}withMasking' directories for results vs pile-up"
mkdir -p $wwwdir/$ERA/TrendPlots/vsPU
python3 python/DrawHitEfficiencyVsLumi.py $ERA ${DIR}withMasking 1
StoreTrendPlotsOutput SiStripHitEffTrendPlotVsPU $ERA vsPU


echo "Done."
