_stack_completion() {
	local loc cur opts BASE_DIR

	# BASE_DIR represents the path to the directory containing
	# all the possible commands in their directories.
	BASE_DIR="/opt/stack/lib/python3.*/site-packages/stack/commands/"

	# Currently typed word
	cur="${COMP_WORDS[COMP_CWORD]}"

	if [[ "$cur" = "=" ]]; then
		loc=${BASE_DIR}
	else
		# Generate directory path from the input command line,
		# excluding the first word (stack)
		loc=${BASE_DIR}"$(tr -s ' ' '/' <<< ${COMP_WORDS[@]:1})"
	fi

	# Make sure that loc is actually path to a directory
	if [[ ! -d ${loc} ]]; then
		if [[ -n ${cur} ]]; then
			loc=$(echo ${loc} | rev | cut -d/ -f2- | rev)
		else
			return
		fi
	fi

	# Generate options, depending on loc
	opts=$(find ${loc} -maxdepth 1 -mindepth 1 -type d -exec basename '{}' \; 2> /dev/null)
	opts+=" --debug"

	# Peel off results, like "__pycache__"
	opts=$(tr -s ' ' '\n' <<< $opts | grep -v "__pycache__")

	# Finally, generate matched results given the options and the current user input.
	COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
}

complete -o default -F _stack_completion stack