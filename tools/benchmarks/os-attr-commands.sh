#!/bin/bash

RUNS=1
if [[ ! -z "$1" ]]
then
    RUNS=$1
fi

if [[ -f "/etc/SuSE-release" ]]
then
    OS="sles"
else
    OS="redhat"
fi

NDX=0
for RUN in $(seq 1 $RUNS)
do
    echo
    echo "*****     RUN $RUN     *****"
    echo

    for NUM_ATTRS in 1 10 100 1000
    do
        attrs[$NDX]=$NUM_ATTRS

        echo "$(date +'%Y-%m-%d %H:%M:%S') - Setting $NUM_ATTRS os attrs..."
        START=$(date +%s.%N)
        for ((i=0 ; i < $NUM_ATTRS ; i++))
        do
            if [[ $i -eq 0 ]]
            then
                FIRST=$(date +%s.%N)
            fi

            if [[ $i -eq $((NUM_ATTRS-1)) ]]
            then
                LAST=$(date +%s.%N)
            fi

            stack set os attr $OS attr=test.$i value=value_$i

            if [[ $i -eq 0 ]]
            then
                first_set_attr_elapsed[$NDX]=$(date +%s.%N --date="$FIRST seconds ago")
            fi

            if [[ $i -eq $((NUM_ATTRS-1)) ]]
            then
                last_set_attr_elapsed[$NDX]=$(date +%s.%N --date="$LAST seconds ago")
            fi
        done
        all_set_attr_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
        echo

        echo "$(date +'%Y-%m-%d %H:%M:%S') - Listing specific os attr..."
        stack set os attr $OS attr=specific_attr value=specific_value
        START=$(date +%s.%N)
        stack list os attr $OS attr=specific_attr >/dev/null
        list_attr_specific_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
        echo

        echo "$(date +'%Y-%m-%d %H:%M:%S') - Listing $NUM_ATTRS os attrs via glob..."
        START=$(date +%s.%N)
        stack list os attr $OS attr='test.*' >/dev/null
        list_attr_glob_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
        echo

        echo "$(date +'%Y-%m-%d %H:%M:%S') - Listing all os attrs..."
        START=$(date +%s.%N)
        stack list os attr $OS >/dev/null
        list_attr_all_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
        echo

        echo "$(date +'%Y-%m-%d %H:%M:%S') - Removing specific os attr..."
        START=$(date +%s.%N)
        stack remove os attr $OS attr=specific_attr
        remove_attr_specific_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
        echo

        echo "$(date +'%Y-%m-%d %H:%M:%S') - Removing $NUM_ATTRS os attrs via glob..."
        START=$(date +%s.%N)
        stack remove os attr $OS attr='test.*'
        remove_attr_glob_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
        echo

        (( NDX++ ))
    done
done

# Output the data
echo "attrs,\
set os attr - first,set os attr - last,set os attr - total,\
list os attr - specific,list os attr - glob,list os attr - all,\
remove os attr - specific,remove os attr - glob"

for ((i=0 ; i < $NDX ; i++))
do

echo "${attrs[$i]},\
${first_set_attr_elapsed[$i]},${last_set_attr_elapsed[$i]},${all_set_attr_elapsed[$i]},\
${list_attr_specific_elapsed[$i]},${list_attr_glob_elapsed[$i]},${list_attr_all_elapsed[$i]},\
${remove_attr_specific_elapsed[$i]},${remove_attr_glob_elapsed[$i]}"

done
