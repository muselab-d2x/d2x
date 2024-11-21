#!/bin/bash

parse_metadata_deletions() {
    local log_content="$1"
    local deletions=()
    local deletion_section=false

    while IFS= read -r line; do
        if [[ "$line" == *"Deleting metadata:"* ]]; then
            deletion_section=true
            continue
        fi
        if $deletion_section; then
            if [[ -z "$line" ]]; then
                break
            fi
            if [[ "$line" =~ ^[[:space:]]*([[:alnum:]]+):[[:space:]]*([[:alnum:]]+)$ ]]; then
                local metadata_type="${BASH_REMATCH[1]}"
                local metadata_name="${BASH_REMATCH[2]}"
                deletions+=("{\"type\":\"$metadata_type\",\"name\":\"$metadata_name\"}")
            fi
        fi
    done <<< "$log_content"

    echo "[${deletions[*]}]"
}

log_content=$(cat)
parse_metadata_deletions "$log_content"
