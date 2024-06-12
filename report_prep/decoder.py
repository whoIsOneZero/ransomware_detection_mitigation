import json
import os

# Load report file
with open('report.json', 'r') as file:
    cuckoo_report = json.load(file)

# Return empty dictionary if it doesn't exist
behavior = cuckoo_report.get('behavior', {})
summary = behavior.get('summary', {})

# Mapping of original keys to new keys
key_mapping = {
    "file_opened": "FILES:OPENED:",
    "regkey_opened": "REG:OPENED:",
    "regkey_written": "REG:WRITTEN:",
    "regkey_deleted": "REG:DELETED:",
    "file_read": "FILES:READ:",
    "regkey_read": "REG:READ:",
    "file_created": "DROP:",
    "file_written": "FILES:WRITTEN:",
    "directory_created": "DIR:CREATED:",
    "file_deleted": "FILES:DELETED:",
    "directory_enumerated": "DIR:ENUMERATED:"
}

 # Helper function to get file extensions
def get_extension(file_path):
    _, ext = os.path.splitext(file_path)
    return ext if ext else None

# Open the output file for writing
with open('extracted.txt', 'w') as outfile:
    for original_key, new_key in key_mapping.items():
        values = summary.get(original_key, [])
        
        # Write each value under the new key
        for value in values:
            outfile.write(f"{new_key}{value}\n")
        
        # If specific keys require extensions to be written
        if original_key in ["file_opened", "file_read", "file_created", "file_written", "file_deleted"]:
            ext_key = new_key.replace("FILES", "FILES_EXT")

            extensions = [get_extension(value) for value in values if get_extension(value)]
            if extensions:
                for ext in extensions:
                    outfile.write(f"{ext_key}{ext}\n")
        
        # Add a newline for readability between different keys
        outfile.write("\n")