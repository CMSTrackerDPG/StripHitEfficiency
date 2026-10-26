# Tools and recipe to produce results for a fill from DQM files:

Before anything type `voms-proxy-init -voms cms -rfc` to have access to the files.

## Produce the results using HTCondor

`./launch_fill_analysis_batch.sh FILLNUMBER`

One single job is sent to harvest all the DQM files content.
It uses the `job_dqmfiles.sub` file and the `cmsRun_batch_eos_dqmfiles` script for the job on HTCondor and results are stored in the directory *Fill_FILLNUMBER_temp*.
 
## Do some post-processing

Done for producing the usual plots and files. It produces also a version of the results with inefficient modules masking. Results are stored in the directory *Fill_FILLNUMBER*.

`./output_postprocessing_for_fill_analysis_batch_dqmfiles.sh Fill_FILLNUMBER_temp`

The usual automatic masking is used and results stored in a *withMasking* directory. A second version of masking that is stronger is also run and the results stored in *withStrongMasking*. In this last one the additionnal inefficient modules printed in the log file `EfficiencyResults_fillFILLNUMBER.txt` are used (up to 8% above the layer threshold usually used). Caveat: in some cases it could be too much.

