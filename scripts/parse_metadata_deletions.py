import re
import json

def parse_metadata_deletions(log_content):
    deletions = []
    deletion_section = False

    for line in log_content.splitlines():
        if "Deleting metadata:" in line:
            deletion_section = True
            continue
        if deletion_section:
            if line.strip() == "":
                break
            match = re.match(r"\s*(\w+):\s*(\w+)", line)
            if match:
                metadata_type, metadata_name = match.groups()
                deletions.append({"type": metadata_type, "name": metadata_name})

    return json.dumps(deletions)
