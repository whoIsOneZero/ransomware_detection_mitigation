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
3. **Cuckoo Sandbox**: Follow the tutorial here to setup your Cuckoo Sandbox
  ```https://beginninghacking.net/2022/11/16/how-to-setup-your-own-malware-analysis-box-cuckoo-sandbox/```

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

5. **Start the Cuckoo Sandbox System**:  
  In the Ubuntu VM;
  - Activate the virtual environment  
  ```sh
  workon sandbox
  ```
  - This script creates a VirtualBox host-only network interface called vboxnet0, which is used for communication between the host and the virtual machines.  
  ```sh
  vmcloak-vboxnet0
  ```
  - Enable IP forwarding on your network interface  
  ```sh
  sudo sysctl -w net.ipv4.conf.enp0s3.forwarding=1
  ```
  - Configures Network Address Translation (NAT) to allow virtual machines in the 192.168.56.0/24 network to access the internet through the enp0s3 interface.  
  ```sh
  sudo iptables -t nat -A POSTROUTING -o enp0s3 -s 192.168.56.0/24 -j MASQUERADE
  ```
  - Set the default policy for the FORWARD chain to DROP, which means all forwarded packets will be dropped unless explicitly allowed.  
  ```sh
  sudo iptables -P FORWARD DROP
  ```
  - Allow packets that are part of an established connection or related to an existing connection.  
  ```sh
  sudo iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
  sudo iptables -A FORWARD -s 192.168.56.0/24 -j ACCEPT
  ```
  <!-- ```sudo iptables -A FORWARD -s 192.168.56.0/24 -j ACCEPT``` -->

  Open Terminator and split into 3 windows
  - Activate the virtual environment in all 3 windows:  
  ```sh
  workon sandbox
  ```
  - In the Terminator window 1, start the Cuckoo rooter service:  
  ```sh
  cuckoo rooter --sudo --group osboxes
  ```
  - In the Terminator window 2, start the main Cuckoo service:  
  ```sh
  cuckoo
  ```
  <!-- - In the Terminator window 3, start the Cuckoo web interface:
  window 3 - cuckoo web --host 127.0.0.1 --port 8080 -->
  - Run this command to get your VM's IP adress of the the primary network interface connected to your VirtualBox's virtual network.
  ```sh
  ip -4 addr show enp0s3 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'
  ```  
  - In the Terminator window 3, start the Cuckoo REST API server on VM's IP address:
  ```sh
  cuckoo api --host 192.168.153.41 --port 8090
  ```

6. **Run the Streamlit App**:  
  On your host machine;
   - Start the Streamlit app using the `streamlit run` command followed by the name of your main Python script (e.g., `main.py`).
     ```sh
     streamlit run main.py
     ```

6. **Access the App in a Web Browser**:  
  On your host machine;
   - Once the app is running, Streamlit will provide a local URL (typically `http://localhost:8501`). Open this URL in a web browser to access your chatbot-powered data analysis tool.


## More
- Cuckoo Docs:
```https://cuckoo.readthedocs.io/en/latest/```
- Complete guide for setting up and running Cuckoo sandbox locally:
```https://beginninghacking.net/2022/11/16/how-to-setup-your-own-malware-analysis-box-cuckoo-sandbox/```

## Troubleshooting
- Cannot start nested win7 VM in Ubuntu VM
```https://forums.virtualbox.org/viewtopic.php?t=87752``` 
- Setup VirtualBox to be able to communicate with the Cuckoo API from teh host machine:
```https://stackoverflow.com/questions/31922055/bridged-networking-not-working-in-virtualbox-under-windows-10```
- Shared folder:
```https://www.makeuseof.com/how-to-create-virtualbox-shared-folder-access/```
