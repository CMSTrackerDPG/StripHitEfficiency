# Tools and recipe to produce results for a fill:

## Use OMS to list the fills

`https://cmsoms.cern.ch`

## Check the quality of data in a fill

`./check_fill_runregistry.sh FILLNUMBER`

It queries the Run Registry and list the runs from the fill with their certification for the ExpressStream and their statistics.
It prints a summary of the fraction of the fill flagged as good.
It uses `getRunsInFill.py` to query the Run Registry with the runregistry python package that can be installed with: `pip install runregistry`.

## RunRegistry export

In case it is not possible to send queries to the RunRegistry, an alternative is to export some content from the RunRegistry page in csv format.

The useful data from the csv file can be extracted with `prepareRunsDatabase.py` and stored in the `data/runs_database.txt` file.
`getRunsInFill_FromFile.py` helps to sparse this output.


## Check the number of calibTree files available for the fill (optional)

`./list_fill_files.sh FILLNUMBER`

It prints the list of the files of the good runs for the fill in a format that can be included in the cfg file.
It uses `list_run_files.sh`.


## Codes to produce the results are in the directory `From_CalitTree_Files` and `From_DQM_Files` depending on the data formats to run on
