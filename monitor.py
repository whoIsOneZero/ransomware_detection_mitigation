import os
from dir_monitor import handler
from cuckoo_client import CuckooAPI
from feature_extraction import get_features, encoding
import time
from datetime import datetime
import classify.classifier as classifier
import json

# Define the directory where files will be saved
save_directory = os.path.join(os.getcwd(), "tmp", "uploads")
reports_directory = os.path.join(os.getcwd(), "reports")
extracted_directory = os.path.join(os.getcwd(), "extracted")
encoding_directory = os.path.join(os.getcwd(), "encodings")

classify = classifier.RansomwareClassifer("test/svm_model.joblib")

warning_mesage = """Ransomware Detected!
                \nWarning: A ransomware sample has been detected on your system.
                Please take the following actions immediately:
                \n1. Disconnect from the internet.
                \n2. Do not open any suspicious files.
                \n3. Run a full system scan using your antivirus software.
                \n4. Contact your IT administrator for further assistance.
                """


def handle_sample(file_path):
    cuckoo_api = CuckooAPI()
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

        # Fetch the report
        report = cuckoo_api.get_report(task_id)
        if report:
            report_path = os.path.join(
                reports_directory, "{}_report.json".format(uploaded_file.name)
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
            encoding_directory, features_file_path, uploaded_file.name
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


if __name__ == "__main__":
    # Choose the directory to monitor
    directory_to_monitor = os.path.expanduser("~/Downloads")

    print(f"{directory_to_monitor} is being monitored")

    # Start monitoring the directory and submit new files
    handler.start_monitoring(directory_to_monitor, handle_sample)
