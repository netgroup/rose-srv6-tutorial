#!/bin/bash

function source_file_if_defined()
{
	local fname="$1"

	if [ -z "${fname+x}" ]; then
		# variable not defined
		return 0;
	fi

	# shellcheck source=/dev/null
	source "${fname}" || return $?

	return 0
}
