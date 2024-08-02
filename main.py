import os
import streamlit as st
import time
import json
from cuckoo_client import CuckooAPI
from feature_extraction import get_features, encoding
import classify.classifier as classifier
from datetime import datetime

CUCKOO_API_URL = "http://192.168.153.41:8090"
API_KEY = "F5DMfnGruS8WgaXIAhbVFg"

# Define the directory where files will be saved
save_directory = os.path.join(os.getcwd(), "tmp", "uploads")
reports_directory = os.path.join(os.getcwd(), "reports")
extracted_directory = os.path.join(os.getcwd(), "extracted")
encoding_directory = os.path.join(os.getcwd(), "encodings")

classify = classifier.RansomwareClassifer("test/svm_model.joblib")


def main():
    st.title("Ransomware Detector")

    # Initialize CuckooAPI
    cuckoo_api = CuckooAPI()

    # Ensure the directory exists
    os.makedirs(save_directory, exist_ok=True)
    os.makedirs(reports_directory, exist_ok=True)
    os.makedirs(extracted_directory, exist_ok=True)
    os.makedirs(encoding_directory, exist_ok=True)

    # File upload widget
    uploaded_file = st.file_uploader(
        "Choose a file to analyze",
        type=["exe", "dll", "pdf", "doc", "docx", "bin"],
        accept_multiple_files=False,
    )

    if uploaded_file:
        # Construct the full file path
        file_path = os.path.join(save_directory, uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.write(f"File uploaded: {uploaded_file.name}")

        # Calculate the SHA-256 hash of the file
        file_hash = cuckoo_api.hash_file(file_path)

        # Check if the data exists in Firestore
        existing_data = cuckoo_api.get_data_by_hash(file_hash)
        if existing_data:
            st.write("Data with this hash already exists in Firestore:")
            st.write(existing_data)
            return

        # Submit the file for analysis
        task_id = cuckoo_api.submit_file(file_path)
        if not task_id:
            st.write(
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

        """ features_file_path = "extracted/innosetup-6.3.3.exe.txt"
        # Encode the features
        encoded_file_path = encoding.encode_features(
            encoding_directory, features_file_path, uploaded_file.name
        ) """

        result = classify.classify_sample(encoded_file_path)

        submit_date = datetime.now().isoformat()
        cuckoo_api.save_to_firestore(
            file_hash,
            uploaded_file.name,
            submit_date,
            result,
        )

        st.write("Classification completed and data saved to Firestore.")


if __name__ == "__main__":
    main()
