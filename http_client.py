import requests
from datetime import datetime

# IP and port configuration for the Red Pitaya HTTP server
RP_IP = "192.168.100.45"
HTTP_PORT = 8000


def set_fpga_register(data):
    """
    Sends a POST request to set a register value in the FPGA.

    Args:
        data (dict): Dictionary containing 'offset', 'value', and 'signed' keys.
    """
    response = requests.post(f"http://{RP_IP}:{HTTP_PORT}/register", json=data)
    print(response.json())

def set_gain(data):
    """
    Sends a POST request to set the gain value(s).

    Args:
        data (dict): Dictionary with the key 'values' and a list of gain values.
    """
    response = requests.post(f"http://{RP_IP}:{HTTP_PORT}/setgain", json=data)
    print(response.json())

def get_file():
    """
    Sends a GET request to download a data log file from the Red Pitaya server.
    Saves the file locally with a timestamped filename.
    """
    response = requests.get(f"http://{RP_IP}:{HTTP_PORT}/download")
    if response.status_code == 200:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data_{timestamp}.txt"
        with open(filename, "wb") as file:
            file.write(response.content)
            print("File downloaded and saved successfully.")
    else:
        print(f"Error downloading file: {response.status_code}")

