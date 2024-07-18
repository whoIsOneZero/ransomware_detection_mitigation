import json
import time
import requests

CUCKOO_API_URL = "http://localhost:8090"
API_KEY = "F5DMfnGruS8WgaXIAhbVFgyour_api_key_here"

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
        return None

def main():
    file_path = raw_input("Enter the path to the file to analyze: ")
    
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
