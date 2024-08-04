# RansomShield: Crypto-Ransomware Detection and Mitigation Tool

RansomShield is a powerful tool designed to detect and mitigate crypto-ransomware using machine learning. This tool utilizes Cuckoo Sandbox for dynamic malware analysis, extracts features from analysis reports, and classifies samples using a trained Support Vector Machine (SVM) model.

| <img src="https://github.com/whoIsOneZero/ransomware_detection_mitigation/blob/main/cerber_analysis.png?raw=true"> |
|:--:| 
| *Sample Analysis* |


## Features

- File upload and analysis using Cuckoo Sandbox.
- Dynamic feature extraction from analysis reports.
- Ransomware classification using a trained SVM model.
- Integration with a cloud-based signature repository.
- User-friendly Streamlit interface for easy usage.

## Prerequisites
1. **Python Installed**: Ensure you have Python 3.10+ installed on your machine.
2. **Oracle VM VirtualBox**: Enusre you're have Oracle VM VirtualBox on a Windows sytem. Download [here](https://www.virtualbox.org/wiki/Downloads)

## Usage

1. **Clone the Repository or Download the Code**:
   - Clone the repository.
     ```sh
     git clone https://github.com/whoIsOneZero/ransomware_detection_mitigation.git
     ```
   - Alternatively, download the project files and extract them to your desired location.

2. **Navigate to the Project Directory**:
   - Open a terminal (or command prompt) and navigate to the directory containing your project files. Example:
     ```sh
     cd C:\Users\user\Desktop\ransomware_detection_mitigation
     ```

3. **Create a Virtual Environment (Optional but Recommended)**:
   - Create a virtual environment to isolate your project dependencies.
     ```sh
     python -m venv myenv
     ```
   - Activate the virtual environment.
     - On Windows:
       ```sh
       myenv\Scripts\activate
       ```
     - On macOS/Linux:
       ```sh
       source myenv/bin/activate
       ```

4. **Install Required Dependencies**:
  - Install all required dependencies using pip. If you have a `requirements.txt` file, use it to install dependencies.
    ```sh
    pip install -r requirements.txt
    ```


5. **Run the Streamlit App**:
   - Start the Streamlit app using the `streamlit run` command followed by the name of your main Python script (e.g., `main.py`).
     ```sh
     streamlit run main.py
     ```

6. **Access the App in a Web Browser**:
   - Once the app is running, Streamlit will provide a local URL (typically `http://localhost:8501`). Open this URL in a web browser to access your chatbot-powered data analysis tool.

<!-- ## Command Summary

```sh
# Step 1: Clone the repository
git clone https://github.com/whoIsOneZero/ransomware_detection_mitigation.git

# Step 2: Navigate to the project directory
cd path/to/your/project

# Step 3: Create a virtual environment (optional)
python -m venv myenv
source myenv/bin/activate  # On macOS/Linux
# myenv\Scripts\activate  # On Windows

# Step 4: Install required dependencies
pip install -r requirements.txt

# Step 5: Run the Streamlit app
streamlit run main.py
``` -->
