import requests
from datetime import datetime

RP_IP = "192.168.100.45"
HTTP_PORT = 8000


def set_fpga_register(data):
    response = requests.post(f"http://{RP_IP}:{HTTP_PORT}/register", json=data)
    print(response.json())

def get_file():
    response = requests.get(f"http://{RP_IP}:{HTTP_PORT}/download")
    if response.status_code == 200:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data_{timestamp}.txt"
        # Guardar el archivo
        with open(filename, "wb") as file:
            file.write(response.content)
            print("Archivo descargado y guardado exitosamente.")
    else:
        print(f"Error al descargar el archivo: {response.status_code}")

