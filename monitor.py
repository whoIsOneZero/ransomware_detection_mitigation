import os
from cuckoo_client import CuckooAPI
from feature_extraction import get_features, encoding
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from datetime import datetime
import classify.classifier as classifier
import json
import numpy as np


class FileMonitorHandler(FileSystemEventHandler):
    def __init__(self, tool):
        self.tool = tool

    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            self.tool(event.src_path)


class DirectoryMonitor:
    def __init__(
        self,
        directory,
        reports_dir="reports",
        encodings_dir="encodings",
        extracted_dir="extracted",
        save_dir="uploads",
    ):
        self.directory = directory
        self.reports_directory = os.path.join(os.getcwd(), reports_dir)
        self.encoding_directory = os.path.join(os.getcwd(), encodings_dir)
        self.extracted_directory = os.path.join(os.getcwd(), extracted_dir)
        self.save_directory = os.path.join(os.getcwd(), "tmp", save_dir)

        # Ensure the directory exists
        os.makedirs(self.save_directory, exist_ok=True)
        os.makedirs(self.reports_directory, exist_ok=True)
        os.makedirs(self.extracted_directory, exist_ok=True)
        os.makedirs(self.encoding_directory, exist_ok=True)

        print(f"{self.directory} is being monitored")

    def start_monitoring(self):
        event_handler = FileMonitorHandler(self.handle_sample)
        observer = Observer()
        observer.schedule(event_handler, path=self.directory, recursive=False)
        observer.start()
        # print(f"Monitoring directory: {self.directory}")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def handle_sample(self, file_path):
        cuckoo_api = CuckooAPI()
        classify = classifier.RansomwareClassifer("test/svm_model.joblib")

        warning_mesage = """Ransomware Detected!
                        \nWarning: A ransomware sample has been detected on your system.
                        Please take the following actions immediately:
                        \n1. Disconnect from the internet.
                        \n2. Do not open any suspicious files.
                        \n3. Run a full system scan using your antivirus software.
                        \n4. Contact your IT administrator for further assistance.
                        """
        print(f"This is the file path/name: {file_path}")

        # End the program for now
        return

        # Submit sample
        task_id = cuckoo_api.submit_file(file_path)

        # Calculate the SHA-256 hash of the file
        file_hash = cuckoo_api.hash_file(file_path)

        # Check if the data exists in Firestore
        existing_data = cuckoo_api.get_data_by_hash(file_hash)
        if existing_data:
            # st.info("\tKnown sample. \nFetching data from signature repository.")

            result = existing_data["is_ransomware"]

            if result == 1:
                print(f"⚠️ {warning_mesage}")
            else:
                print("Non-ransomware sample.")

            print(existing_data)

            return

        if not task_id:
            print(
                "The Cuckoo API has not been started yet or is currently unavailable."
            )
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

            # Fetch the report
            report = cuckoo_api.get_report(task_id)
            if report:
                report_path = os.path.join(
                    self.reports_directory, "{}_report.json".format(uploaded_file.name)
                )
                with open(report_path, "w") as report_file:
                    json.dump(report, report_file, indent=4)
                print("Report saved to {}".format(report_path))

            # Extract the features
            features_file_path = get_features.process_report(
                report_path, uploaded_file.name
            )

            # Encode the features
            encoded_file_path = encoding.encode_features(
                self.encoding_directory, features_file_path, uploaded_file.name
            )

            result = classify.classify_sample(encoded_file_path)

            # Convert the result to an integer if it's a numpy boolean type
            is_ransomware = (
                bool(result) if isinstance(result, (np.bool_, bool)) else int(result)
            )

            submit_date = datetime.now().isoformat()
            cuckoo_api.save_to_firestore(
                file_hash,
                uploaded_file.name,
                submit_date,
                is_ransomware,
            )

            if is_ransomware == 1:
                print(f"⚠️ {warning_mesage}")
            else:
                print("Non-ransomware sample.")

        print("Classification completed and data saved to Firestore.")
