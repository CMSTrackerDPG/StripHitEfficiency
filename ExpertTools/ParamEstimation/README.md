# Tools to determine paramters values used in the predictive model


## Fit the efficiency as a function of the pile-up

`python3 FitEffvsPUTrend.py filename [xmin xmax]`

Get the efficiency measurement as a function of the pile-up in the file provided in argument.
For each layer the curves are fitted with a line. The parameters (offset and slope) are saved in a root file *PUfit.root*.
The PU range to be used for the fit can be precised as optionnal arguments. If not precised, the whole range is used.

## Computation of the deadtime parameter

`python3 ComputeDeadtime.py filename [pileup]`

The deadtime is computed from the output of the previous section and the hip probabilities measured in a dedicated analysis.
The efficiency measurement file is to be provided in argument to allow checks.
By default the average pileup value is read from this file. But a value can be given through an optional argument.
The deadtimes are output in a text file.

