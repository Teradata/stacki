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

    for NUM_ENVIRONMENTS in 1 10 100 1000
    do
        for NUM_ATTRS in 1 10 100
        do
            environments[$NDX]=$NUM_ENVIRONMENTS
            attrs[$NDX]=$NUM_ATTRS

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Adding $NUM_ENVIRONMENTS environments..."
            for ((i=0 ; i < $NUM_ENVIRONMENTS ; i++))
            do
                stack add environment test-$i
            done
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Setting $NUM_ATTRS environment attrs..."
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

                stack set environment attr 'test-%' attr=test.$i value=value_$i

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

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Listing specific environment attr..."
            START=$(date +%s.%N)
            stack list environment attr 'test-%' attr=test.1 >/dev/null
            list_attr_specific_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Listing $NUM_ATTRS environment attrs via glob..."
            START=$(date +%s.%N)
            stack list environment attr 'test-%' attr='test.*' >/dev/null
            list_attr_glob_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Listing all environment attrs..."
            START=$(date +%s.%N)
            stack list environment attr 'test-%' >/dev/null
            list_attr_all_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Removing specific environment attr..."
            stack set environment attr 'test-%' attr=test.specific value=value_specific
            START=$(date +%s.%N)
            stack remove environment attr 'test-%' attr=test.specific
            remove_attr_specific_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Removing $NUM_ATTRS environment attrs via glob..."
            START=$(date +%s.%N)
            stack remove environment attr 'test-%' attr='test.*'
            remove_attr_glob_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Removing $NUM_ENVIRONMENTS environments..."
            stack remove environment 'test-%'
            echo

            (( NDX++ ))
        done
    done
done

# Output the data
echo "environments,attrs,\
set environment attr - first,set environment attr - last,set environment attr - total,\
list environment attr - specific,list environment attr - glob,list environment attr - all,\
remove environment attr - specific,remove environment attr - glob"

for ((i=0 ; i < $NDX ; i++))
do

echo "${environments[$i]},${attrs[$i]},\
${first_set_attr_elapsed[$i]},${last_set_attr_elapsed[$i]},${all_set_attr_elapsed[$i]},\
${list_attr_specific_elapsed[$i]},${list_attr_glob_elapsed[$i]},${list_attr_all_elapsed[$i]},\
${remove_attr_specific_elapsed[$i]},${remove_attr_glob_elapsed[$i]}"

done
