import os
import streamlit as st
import requests
import time
import json
import hashlib

CUCKOO_API_URL = "http://192.168.153.41:8090"
API_KEY = "F5DMfnGruS8WgaXIAhbVFg"

# Define the directory where files will be saved
save_directory = os.path.join(os.getcwd(), 'tmp', 'uploads')

def hash_file(file_path):
    """Calculate the SHA-256 hash of the given file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        file_hash = sha256_hash.hexdigest()
        print("SHA-256 hash of the file: {}".format(file_hash))
        st.write(f"SHA-256 hash of the file: {file_hash}")
        return file_hash
    except IOError as e:
        print("Error reading file {}: {}".format(file_path, e))
        st.error(f"Error reading file {file_path}: {e}")
        return None

def submit_file(file_path):
    """Submit a file to Cuckoo for analysis."""
    headers = {"Authorization": "Bearer {}".format(API_KEY)}
    try:
        with open(file_path, "rb") as file:
            files = {"file": file}
            response = requests.post("{}/tasks/create/file".format(CUCKOO_API_URL), files=files, headers=headers)
            response.raise_for_status()
            task_id = response.json().get("task_id")
            print("File submitted successfully. Task ID: {}".format(task_id))
            return task_id
    except requests.exceptions.RequestException as e:
        print("Error submitting file: {}".format(e))
        st.error(f"Error submitting file: {e}")
        return None

def get_task_status(task_id):
    """Check the status of a task."""
    headers = {"Authorization": "Bearer {}".format(API_KEY)}
    try:
        response = requests.get("{}/tasks/view/{}".format(CUCKOO_API_URL, task_id), headers=headers)
        response.raise_for_status()
        task_status = response.json().get("task", {}).get("status")
        return task_status
    except requests.exceptions.RequestException as e:
        print("Error fetching task status: {}".format(e))
        st.error(f"Error fetching task status: {e}")
        return None

def get_report(task_id):
    """Retrieve the analysis report."""
    headers = {"Authorization": "Bearer {}".format(API_KEY)}
    try:
        response = requests.get("{}/tasks/report/{}".format(CUCKOO_API_URL, task_id), headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching report: {}".format(e))
        st.error(f"Error fetching report: {e}")
        return None

def main():
    st.title("Ransomware Detector")


    # Ensure the directory exists
    os.makedirs(save_directory, exist_ok=True)

    # File upload widget
    uploaded_file = st.file_uploader("Choose a file to analyze", type=["exe", "dll", "pdf", "doc", "docx"])
    
    if uploaded_file:
        # Construct the full file path
        file_path = os.path.join(save_directory, uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.write(f"File uploaded: {uploaded_file.name}")
    
        # Calculate the SHA-256 hash of the file
        file_hash = hash_file(file_path)

    
        # Submit the file for analysis
        task_id = submit_file(file_path)
        if not task_id:
            return

        # Check the status of the analysis
        while True:
            status = get_task_status(task_id)
            if status == "reported":
                print("Analysis completed for task ID: {}".format(task_id))
                break
            elif status == "completed":
                print("Analysis completed for task ID: {}, waiting for report generation.".format(task_id))
            else:
                print("Current status of task ID {}: {}".format(task_id, status))
            time.sleep(10)

        # Fetch the report
        report = get_report(task_id)
        if report:
            report_path = "report_{}.json".format(task_id)
            with open(report_path, "w") as report_file:
                json.dump(report, report_file, indent=4)
            print("Report saved to {}".format(report_path))

if __name__ == "__main__":
    main()
