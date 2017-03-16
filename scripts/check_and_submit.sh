#!/bin/bash

DATA_DIR=data

find $DATA_DIR -name 'm-*.txt' | while read FNAME
do
    INRUN="${FNAME}.inrun"
    PNEW=${FNAME/m-/p_new-}
    echo -n "[$FNAME] "
    if [ -f "$INRUN" ]; then
        SLURM_ID=$(cat "$INRUN")
        JOBSTATE=$(scontrol show job $SLURM_ID | grep JobState | sed -e 's/.*JobState=//' -e 's/ .*//')
        
        if [ -f "$PNEW" ]; then  # both exist
            if [ "$JOBSTATE" == "COMPLETED" ]; then
                echo "DONE (just now)"
                rm $INRUN
            else
                echo "**ERROR** inrun and p_now but JobState=$JOBSTATE"
            fi
        else # inrun but not p_new
            if [ "$JOBSTATE" == "RUNNING" ]; then
                echo "RUNNING"
            else
                echo "**ERROR** inrun, but no p_now and JobState=$JOBSTATE"
            fi
        fi
    else
        if [ ! -f "$PNEW" ]; then # neither exist
            touch $INRUN

            echo -n "SUBMITTING "
            RES=$(sbatch btl_sbatch.sh $NAME)
            SLURM_ID=${RES##* }
            
            echo "$SLURM_ID"
            echo "$SLURM_ID" > $INRUN
        else
            echo "DONE"
        fi
    fi
done

# - rsync from shell
# - foreach video, image:
#     foreach m-*.txt:
#       check if .inrun exists
#       check if p_new exists
#       if neither:
#          touch .inrun - incl slurm id :-)
#          sbatch run
#       if exists and p_new exists:
#          rm .inrun

#       check sync slurmid?
#       sbatch btl_sbatch.sh m-13.txt
