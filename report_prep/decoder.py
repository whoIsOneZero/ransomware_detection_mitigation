import json
import os

# Load report file
with open('report.json', 'r') as file:
    cuckoo_report = json.load(file)

# Return empty dictionary if it doesn't exist
behavior = cuckoo_report.get('behavior', {})
summary = behavior.get('summary', {})
processes = behavior.get('generic', [])
# Extract apistats
apistats = behavior.get('apistats', {})

strings = cuckoo_report.get('strings', {})

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

 # Find the PID for "cerber.exe"
cerber_pid = None
for process in processes:
    if process.get('process_name') == "cerber.exe":
        cerber_pid = process.get('pid')
        break

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
        #outfile.write("\n")
        
    # Write strings to the file
    #outfile.write("STRINGS:\n")
    num = 1
    for string in strings:
        outfile.write(f"STR:{num};{string}\n")
        num = num + 1

    # Write cerber.exe API calls to the file
    if cerber_pid is not None:
        # Write apistats for cerber.exe PID to the file
        cerber_apistats = apistats.get(str(cerber_pid), {})
        #outfile.write(f"API Stats for PID {cerber_pid}:\n")
        for api_call, count in cerber_apistats.items():
            outfile.write(f"API:{api_call}\n")
    else:
        outfile.write("PID for cerber.exe not found\n")