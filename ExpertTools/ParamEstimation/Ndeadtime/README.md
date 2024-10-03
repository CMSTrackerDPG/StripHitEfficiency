# Ndeadtime 

Example for using code for computing deadtime per layer:

`python3 ComputeDeadtime.py ../LowPUOffset/SiStripHitEffHistos_fill8822_perDisk.root`

It will automatically use `../LowPUOffset/PUFit_fill8822_perDisk.root` created in the previous step (LowPUOffset).

It needs also as input the HIP probability as save in `../../PredictionsModel/inputs/archive/HIPProbPerPU_perDisk_mergedSides.root` for example.
