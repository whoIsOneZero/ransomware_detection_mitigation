import os
import streamlit as st
import time
import json
from cuckoo_client import CuckooAPI
from feature_extraction import get_features, encoding
import classify.classifier as classifier
from datetime import datetime
import numpy as np

CUCKOO_API_URL = "http://192.168.153.41:8090"
API_KEY = "F5DMfnGruS8WgaXIAhbVFg"

st.set_page_config(
    page_title="RansomShield",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

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


def main():

    # Centered title using HTML in Markdown
    st.markdown(
        f"""
        <h1 style='text-align: center;'>Crypto-Ransomware <br/> Detection Tool</h1>
        """,
        unsafe_allow_html=True,
    )

    # st.title("Ransomware Detection Tool")

    # Centered title with image on the same line

    # Initialize CuckooAPI
    cuckoo_api = CuckooAPI()

    # Ensure the directory exists
    os.makedirs(save_directory, exist_ok=True)
    os.makedirs(reports_directory, exist_ok=True)
    os.makedirs(extracted_directory, exist_ok=True)
    os.makedirs(encoding_directory, exist_ok=True)

    # File upload widget
    uploaded_file = st.file_uploader(
        "Select sample",
        type=["exe", "dll", "pdf", "doc", "docx", "bin"],
        accept_multiple_files=False,
    )

    if uploaded_file:
        # Construct the full file path
        file_path = os.path.join(save_directory, uploaded_file.name)

        # Temporarily display the message while executing the block of code
        with st.spinner("Analyzing file..."):

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            # st.write(f"File uploaded: {uploaded_file.name}")

            # Calculate the SHA-256 hash of the file
            file_hash = cuckoo_api.hash_file(file_path)

            # Check if the data exists in Firestore
            existing_data = cuckoo_api.get_data_by_hash(file_hash)
            if existing_data:
                # st.info("\tKnown sample. \nFetching data from signature repository.")

                result = existing_data["is_ransomware"]

                if result == 1:
                    st.warning(
                        warning_mesage,
                        icon="⚠️",
                    )
                else:
                    st.info("Non-ransomware sample.")

                st.write(existing_data)

                return
            # else: st.write("The sample will be analyzed") """

        with st.spinner("Analyzing file..."):
            # Temporarily display the message while executing the block of code

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
                st.warning(
                    warning_mesage,
                    icon="⚠️",
                )
            else:
                st.info("Non-ransomware sample.")

        st.write("Classification completed and data saved to Firestore.")


if __name__ == "__main__":
    main()
