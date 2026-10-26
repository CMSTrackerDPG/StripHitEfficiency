#!/bin/sh

#FILE=data/runs_database.txt
FILE=$2

while read RUN DATASET_TYPE DATASET FILL PIX STRIP TRACKING TRIGGERS
do
  if [ "$FILL" == "$1" ]
  then
     echo "$RUN $DATASET_TYPE $DATASET $FILL $PIX $STRIP $TRACKING $TRIGGERS"
  fi
done < $FILE

