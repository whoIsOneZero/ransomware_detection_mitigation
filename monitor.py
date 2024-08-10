import os
from dir_monitor import handler
from cuckoo_client import CuckooAPI
import time


def handle_sample(file_path):
    cuckoo_api = CuckooAPI()
    task_id = cuckoo_api.submit_file(file_path)

    if not task_id:
        print("The Cuckoo API has not been started yet or is currently unavailable.")
        return

    # Check the status of the analysis
    while True:
        status = cuckoo_api.get_task_status(task_id)
        if status == "reported":
            print("Analysis completed for task ID: {}".format(task_id))
            break
        elif status == "completed":
            print(
                "Analysis completed for task ID: {}, waiting for report generation.".format(
                    task_id
                )
            )
        else:
            print("Current status of task ID {}: {}".format(task_id, status))
        time.sleep(10)


if __name__ == "__main__":
    # Choose the directory to monitor
    directory_to_monitor = os.path.expanduser("~/Downloads")

    print(f"{directory_to_monitor} is being monitored")

    # Start monitoring the directory and submit new files
    handler.start_monitoring(directory_to_monitor, handle_sample)
