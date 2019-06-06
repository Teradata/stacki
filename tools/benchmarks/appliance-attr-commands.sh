#!/bin/bash

RUNS=1
if [[ ! -z "$1" ]]
then
    RUNS=$1
fi

NDX=0
for RUN in $(seq 1 $RUNS)
do
    echo
    echo "*****     RUN $RUN     *****"
    echo

    for NUM_APPLIANCES in 1 10 100 1000
    do
        for NUM_ATTRS in 1 10 100
        do
            appliances[$NDX]=$NUM_APPLIANCES
            attrs[$NDX]=$NUM_ATTRS

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Adding $NUM_APPLIANCES appliances..."
            for ((i=0 ; i < $NUM_APPLIANCES ; i++))
            do
                stack add appliance test-$i
            done
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Setting $NUM_ATTRS appliance attrs..."
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

                stack set appliance attr 'test-%' attr=test.$i value=value_$i

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

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Listing specific appliance attr..."
            START=$(date +%s.%N)
            stack list appliance attr 'test-%' attr=test.1 >/dev/null
            list_attr_specific_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Listing $NUM_ATTRS appliance attrs via glob..."
            START=$(date +%s.%N)
            stack list appliance attr 'test-%' attr='test.*' >/dev/null
            list_attr_glob_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Listing all appliance attrs..."
            START=$(date +%s.%N)
            stack list appliance attr 'test-%' >/dev/null
            list_attr_all_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Removing specific appliance attr..."
            stack set appliance attr 'test-%' attr=test.specific value=value_specific
            START=$(date +%s.%N)
            stack remove appliance attr 'test-%' attr=test.specific
            remove_attr_specific_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Removing $NUM_ATTRS host attrs via glob..."
            START=$(date +%s.%N)
            stack remove appliance attr 'test-%' attr='test.*'
            remove_attr_glob_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Removing $NUM_APPLIANCES appliances..."
            stack remove appliance 'test-%'
            echo

            (( NDX++ ))
        done
    done
done

# Output the data
echo "appliances,attrs,\
set appliance attr - first,set appliance attr - last,set appliance attr - total,\
list appliance attr - specific,list appliance attr - glob,list appliance attr - all,\
remove appliance attr - specific,remove appliance attr - glob"

for ((i=0 ; i < $NDX ; i++))
do

echo "${appliances[$i]},${attrs[$i]},\
${first_set_attr_elapsed[$i]},${last_set_attr_elapsed[$i]},${all_set_attr_elapsed[$i]},\
${list_attr_specific_elapsed[$i]},${list_attr_glob_elapsed[$i]},${list_attr_all_elapsed[$i]},\
${remove_attr_specific_elapsed[$i]},${remove_attr_glob_elapsed[$i]}"

done
