#! /bin/bash
set -x
declare -a nodes
while true
do
	case "$1" in
		-n|--node) nodes+=("$2"); shift 2;;
		--) shift; break;;
		*) break;;
	esac
done

if !(( ${#nodes[@]} ))
	then
		echo "at least one -n or --node is required"
		exit 1
fi

# Switch back to the standard sles11 partition scheme
/opt/stack/bin/stack load storage partition file=/export/csv/td-part-sles11.csv

# Reinstall each node to sles 11 to clean up after a move op.
/opt/stack/bin/stack set host bootaction "${nodes[@]}" action="install sles 11.3 console" type=install
/opt/stack/bin/stack set host box "${nodes[@]}" box=sles11
/opt/stack/bin/stack set host boot "${nodes[@]}" action=install nukedisks=true nukecontroller=true
/opt/stack/bin/stack set host power "${nodes[@]}" command=reset debug=true
