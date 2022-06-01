# Tools used by shifters

## HitEffDriver.sh

`./HitEffDriver.sh -e ERA -n NFILES RUNNUMBER`

It produces the hit efficiency results for a given run and store the results in a web directory. It uses the files `template/SiStripHitEff_template.py`, `template/template_SiStripHitEffBadModules.txt`. 
The results are made from calibration tree files produced from Express AlcaReco and stored on EOS. The analysis is run on few files only per run to save time.
A pre-analysis of the pile-up is run for removing tree files with large PU variations. Then the analysis is done twice. The second time the very inefficient modules are masked.
The results are compared with a predictive model. At the end trend plots are produced with`TrendPlots.sh`.

## TrendPlots.sh

`./TrendPlots.sh ERA`

The script produces trend plots of the efficiency in a layer computed run by run. ERA is the name of the web directory where the runs results are stored like 'GR18'. The trend plots are stored in the same directory.
The plots are produced by the scripts `DrawHitEfficiencyVsRun.py` and `DrawHitEfficiencyVsLumi.py` as a function of the run number and as a function of the luminosity or the pile-up.

## SiStripHitEff_CompareRuns.C

`root -l`
`.X SiStripHitEff_CompareRuns.C("ERA1","RUN1","ERA2","RUN2")`

Macro to compare the results of 2 runs. It produces 2 plots one with the curves for all the modules and one with only the good modules.

