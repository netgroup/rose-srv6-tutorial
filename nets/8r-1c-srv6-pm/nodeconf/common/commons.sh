#!/bin/bash

function source_file_if_defined()
{
	local fname="$1"
	local res

	if [ -z "${fname+x}" ]; then
		# variable not defined
		return 0;
	fi

	source "${fname}" || return $?

	return 0
}
