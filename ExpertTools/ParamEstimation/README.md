# Model Parameters Estimation

This package gather different codes for computing the various inputs needed for the prediction model. They have to be determined in the order presented below.


## LowPUOffset

This first step uses curves of the hit efficiency as a function of pile-up to extract the intercept and the slope.

`python3 FitEffvsPUTrend.py FILLNUMBER`


## Ndeadtime

The slope extracted in previous step is divided by the HIP probability to deduce a deadtime. The value is given in bunch-crossing unit.

`python3 ComputeDeadtime.py FILE [PU]`

If the average pile-up is not provided, the average value found in one histogram of the input file is used.

In case Ndeadtime is needed per disk in the endcap part, a conversion from the HIP probability per ring can be made:

`python3 RecomputeHIPprob.py`


## factReweight

A weight is computed based on the beam filling scheme of the fill used for computing the deadtime.

`python3 ComputeFillWeight.py`

It uses as input the deadtimes per layer in `Ndeadtime.txt` and the filling scheme in `fill.json`.
