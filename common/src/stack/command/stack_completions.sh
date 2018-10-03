_stack_completion() {
	local loc cur opts BASE_DIR

	# BASE_DIR represents the path to the directory containing
	# all the possible commands in their directories.
	BASE_DIR="./stack/commands/"

	# Currently typed word
	cur="${COMP_WORDS[COMP_CWORD]}"

	# Generate directory path from the input command line,
	# excluding the first word (stack)
	loc=${BASE_DIR}"$(tr -s ' ' '/' <<< ${COMP_WORDS[@]:1})"

	# Make sure that loc is actually path to a directory
	if [[ ! -d ${loc} ]]; then
		if [[ -n ${cur} ]]; then
			loc=$(echo ${loc} | rev | cut -d/ -f2- | rev)
		else
			return
		fi
	fi
	# Generate options, depending on loc
	opts=$(find ${loc} -maxdepth 1 -mindepth 1 -type d -exec basename '{}' \;)
	opts+=" --debug --version --help"

	# Finally, generate matched results given the options and the current user input.
	COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
}

complete -o default -F _stack_completion stack