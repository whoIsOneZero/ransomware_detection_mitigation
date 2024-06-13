import json
import os

# Set to keep track of seen extensions
seen_extensions = set()

# Load report file
def load_report(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Helper function to get file extensions and avoid duplicates
def get_extension(file_path):
    _, ext = os.path.splitext(file_path)
    if ext and ext not in seen_extensions:
        seen_extensions.add(ext)
        return ext
    return None

# Helper function to write summary data to the file
def write_summary_data(outfile, summary, key_mapping):
    for original_key, new_key in key_mapping.items():
        values = summary.get(original_key, [])
        
        # Write each value under the new key
        for value in values:
            outfile.write(f"{new_key}{value}\n")
        
        # If specific keys require extensions to be written
        if original_key in ["file_opened", "file_read", "file_created", "file_written", "file_deleted"]:
            ext_key = "DROP:" if original_key == "file_created" else new_key.replace("FILES", "FILES_EXT")

            # Reset seen_extensions before processing current_key
            seen_extensions.clear()

            extensions = [get_extension(value) for value in values]
            
            # Write extensions if they exist
            for ext in filter(None, extensions):
                outfile.write(f"{ext_key}{ext}\n")

# Helper function to write strings to the file
def write_strings(outfile, strings):
    for string_num, string in enumerate(strings, start=1):
        outfile.write(f"STR:{string_num};{string}\n")

# Main function
def main():
    cuckoo_report = load_report('report.json')

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

    # Find the PID for the sample program
    sample_pid = next((process.get('pid') for process in processes if process.get('process_name') == "cerber.exe"), None)

    # Open the output file for writing
    with open('extracted.txt', 'w') as outfile:
        # Write API calls made by sample to the file
        if sample_pid is not None:
            sample_apistats = apistats.get(str(sample_pid), {})
            for api_call in sample_apistats:
                outfile.write(f"API:{api_call}\n")
        else:
            outfile.write("PID for cerber.exe not found\n")

        # Write summary data
        write_summary_data(outfile, summary, key_mapping)

        # Write strings data
        write_strings(outfile, strings)

# Execute main function
if __name__ == "__main__":
    main()
