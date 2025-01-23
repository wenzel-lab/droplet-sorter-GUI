import requests

RP_IP = "192.168.100.45"
HTTP_PORT = 8000


def set_fpga_register(data):
    response = requests.post(f"http://{RP_IP}:{HTTP_PORT}/register", json=data)
    print(response.json())

