import requests
import hashlib
import firebase_admin
from firebase_admin import credentials, firestore
import numpy as np

"""
This code is to be used outside the Ubuntu VM
"""

# CUCKOO_API_URL = "http://192.168.153.41:8090"
CUCKOO_API_URL = "http://192.168.198.41:8090"
API_KEY = "F5DMfnGruS8WgaXIAhbVFg"


class CuckooAPI:
    def __init__(self):
        self.api_url = CUCKOO_API_URL
        self.api_key = API_KEY
        self.headers = {"Authorization": f"Bearer {API_KEY}"}

        # Initialize Firebase only if it hasn't been initialized yet
        if not len(
            firebase_admin._apps
        ):  # Check if Firebase apps have been initialized
            cred = credentials.Certificate("service_account_key.json")
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

        # Initialize Firebase
        # cred = credentials.Certificate("service_account_key.json")
        # firebase_admin.initialize_app(cred)
        # self.db = firestore.client()

    def hash_file(self, file_path):
        """Calculate the SHA-256 hash of the given file."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            file_hash = sha256_hash.hexdigest()
            print("SHA-256 hash of the file: {}".format(file_hash))
            return file_hash
        except IOError as e:
            print("Error reading file {}: {}".format(file_path, e))
            return None

    def get_data_by_hash(self, file_hash):
        """Fetch data from Firestore based on the file hash."""
        docs = (
            self.db.collection("signatures")
            .where(field_path="file_hash", op_string="==", value=file_hash)
            .stream()
        )
        for doc in docs:
            return doc.to_dict()
        return None

    def submit_file(self, file_path):
        """Submit a file to Cuckoo for analysis."""
        # headers = {"Authorization": "Bearer {}".format(API_KEY)}
        try:
            with open(file_path, "rb") as file:
                files = {"file": file}
                response = requests.post(
                    "{}/tasks/create/file".format(self.api_url),
                    files=files,
                    headers=self.headers,
                )
                response.raise_for_status()
                task_id = response.json().get("task_id")
                print("File submitted successfully. Task ID: {}".format(task_id))
                return task_id
        except requests.exceptions.RequestException as e:
            print("Error submitting file: {}".format(e))
            return None

    def get_task_status(self, task_id):
        """Check the status of a task."""
        # headers = {"Authorization": "Bearer {}".format(API_KEY)}
        try:
            response = requests.get(
                "{}/tasks/view/{}".format(self.api_url, task_id), headers=self.headers
            )
            response.raise_for_status()
            task_status = response.json().get("task", {}).get("status")
            return task_status
        except requests.exceptions.RequestException as e:
            print("Error fetching task status: {}".format(e))
            return None

    def get_report(self, task_id):
        """Retrieve the analysis report."""
        # headers = {"Authorization": "Bearer {}".format(API_KEY)}
        try:
            response = requests.get(
                "{}/tasks/report/{}".format(self.api_url, task_id), headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print("Error fetching report: {}".format(e))
            return None

    def save_to_firestore(self, file_hash, file_name, submission_date, is_ransomware):
        """Save the analysis data to Firebase Firestore if it doesn't already exist."""

        # Check if the document with the same file_hash exists
        docs = (
            self.db.collection("signatures")
            .where("file_hash", "==", file_hash)
            .stream()
        )
        if any(docs):
            print(f"Data with hash {file_hash} already exists in Firestore.")
            return

        # If the document doesn't exist, add it
        data = {
            "file_hash": file_hash,
            "file_name": file_name,
            "submission_date": submission_date,
            "is_ransomware": is_ransomware,
        }
        self.db.collection("signatures").add(data)
        # print(f"Data saved to Firestore for file: {file_name}")
