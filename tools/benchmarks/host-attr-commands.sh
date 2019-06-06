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

    for NUM_HOSTS in 1 10 100 1000
    do
        for NUM_ATTRS in 1 10 100
        do
            hosts[$NDX]=$NUM_HOSTS
            attrs[$NDX]=$NUM_ATTRS

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Adding $NUM_HOSTS hosts..."
            for ((i=0 ; i < $NUM_HOSTS ; i++))
            do
                stack add host backend-0-$i
            done
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Setting $NUM_ATTRS host attrs..."
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

                stack set host attr 'backend-0-*' attr=test.$i value=value_$i

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

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Listing specific host attr..."
            START=$(date +%s.%N)
            stack list host attr 'backend-0-*' attr=test.1 >/dev/null
            list_attr_specific_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Listing $NUM_ATTRS host attrs via glob..."
            START=$(date +%s.%N)
            stack list host attr 'backend-0-*' attr='test.*' >/dev/null
            list_attr_glob_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Listing all host attrs..."
            START=$(date +%s.%N)
            stack list host attr 'backend-0-*' >/dev/null
            list_attr_all_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Listing host profile..."
            stack set host attr 'backend-0-*' attr=time.servers value=pool.ntp.org
            START=$(date +%s.%N)
            stack list host profile 'backend-0-0' >/dev/null
            list_profile_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Removing specific host attr..."
            START=$(date +%s.%N)
            stack remove host attr 'backend-0-*' attr=time.servers
            remove_attr_specific_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Removing $NUM_ATTRS host attrs via glob..."
            START=$(date +%s.%N)
            stack remove host attr 'backend-0-*' attr='test.*'
            remove_attr_glob_elapsed[$NDX]=$(date +%s.%N --date="$START seconds ago")
            echo

            echo "$(date +'%Y-%m-%d %H:%M:%S') - Removing $NUM_HOSTS hosts..."
            stack remove host 'backend-0-*'
            echo

            (( NDX++ ))
        done
    done
done

# Output the data
echo "hosts,attrs,\
set host attr - first,set host attr - last,set host attr - total,\
list host attr - specific,list host attr - glob,list host attr - all,\
list host profile,\
remove host attr - specific,remove host attr - glob"

for ((i=0 ; i < $NDX ; i++))
do

echo "${hosts[$i]},${attrs[$i]},\
${first_set_attr_elapsed[$i]},${last_set_attr_elapsed[$i]},${all_set_attr_elapsed[$i]},\
${list_attr_specific_elapsed[$i]},${list_attr_glob_elapsed[$i]},${list_attr_all_elapsed[$i]},\
${list_profile_elapsed[$i]},\
${remove_attr_specific_elapsed[$i]},${remove_attr_glob_elapsed[$i]}"

done
