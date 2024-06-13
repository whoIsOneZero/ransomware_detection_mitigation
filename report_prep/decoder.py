import json
import os

# Load report file
with open('report.json', 'r') as file:
    cuckoo_report = json.load(file)

behavior = cuckoo_report.get('behavior', {})
summary = behavior.get('summary', {})
processes = behavior.get('generic', [])
apistats = behavior.get('apistats', {})
strings = cuckoo_report.get('strings', [])

# Mapping of original keys to new keys
key_mapping = {
    "file_opened": "FILES:OPENED:",
    "regkey_opened": "REG:OPENED:",
    "regkey_written": "REG:WRITTEN:",
    "regkey_deleted": "REG:DELETED:",
    "file_read": "FILES:READ:",
    "regkey_read": "REG:READ:",
    "file_created": "FILES:CREATED:",
    "file_written": "FILES:WRITTEN:",
    "directory_created": "DIR:CREATED:",
    "file_deleted": "FILES:DELETED:",
    "directory_enumerated": "DIR:ENUMERATED:"
}

 # Helper function to get file extensions
def get_extension(file_path):
    _, ext = os.path.splitext(file_path)
    return ext if ext else None

 # Find the PID for the sample program
sample_pid = None
for process in processes:
    if process.get('process_name') == "cerber.exe":
        sample_pid = process.get('pid')
        break

# Open the output file for writing
with open('extracted.txt', 'w') as outfile:
    # Write API calls made by sample to the file
    if sample_pid is not None:
        sample_apistats = apistats.get(str(sample_pid), {})
        for api_call, count in sample_apistats.items():
            outfile.write(f"API:{api_call}\n")
    else:
        outfile.write("PID for cerber.exe not found\n")

    # Retrive values from "summary" dictionary using original keys
    for original_key, new_key in key_mapping.items():
        values = summary.get(original_key, [])
        
        # Write each value under the new key
        for value in values:
            outfile.write(f"{new_key}{value}\n")
        
        # If specific keys require extensions to be written
        if original_key in ["file_opened", "file_read", "file_created", "file_written", "file_deleted"]:
            
            # Handle extensions specifically for "file_created"
            if original_key == "file_created":
                ext_key = "DROP:"
            else:
                # create new keys for extensions
                ext_key = new_key.replace("FILES", "FILES_EXT")

            extensions = [get_extension(value) for value in values if get_extension(value)]
            if extensions:
                for ext in extensions:
                    outfile.write(f"{ext_key}{ext}\n")
        
    string_num = 1
    for string in strings:
        outfile.write(f"STR:{string_num};{string}\n")
        string_num += 1