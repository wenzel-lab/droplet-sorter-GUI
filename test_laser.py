import serial

class SerialManager:

    # COM PORT COMMUNICATION

    def __init__(self, port, baud_rate=115200):
        self.port = port
        self.baud_rate = baud_rate
        self.serial_connection = self.init_serial()

    def init_serial(self):
        try:
            ser = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            return ser
        except serial.SerialException as e:
            print(f"Error initializing serial connection: {e}")
            return None

    def send_command(self,command):
        if self.serial_connection:
            try:
                self.serial_connection.write(f'{command}\r\n'.encode())
                response = self.serial_connection.readline().decode().strip()
                return response
            except Exception as e:
                print(f"Error reading from serial: {e}")
                return str(e)
        else:
            print("Serial connection not initialized.")
            return None

    # CHANNEL STATUS

    def get_ch_status(self, channel):
        ch_status = self.send_command(f'GET STATUS {channel}')
        if ch_status and ch_status.startswith('A STATUS'):
            return ch_status.split()[2] # Extract status code
        else:
            return "Unknown"
        
    def get_status_definition(self, binary_code):
        status_definitions = { #Redundant
            0: "Laser Fault",
            1: "Laser Off",
            2: "Laser Emission",
            3: "Laser Ready",
            7: "System Cover Interlock",
        }
        # Ensure the binary code is 8 bits long
        binary_code = binary_code.zfill(8)
        definitions = []

        # Loop through each bit in the binary code
        for bit_position, bit_value in enumerate(reversed(binary_code)):
            if bit_value == '1':
                if bit_position in status_definitions:
                    definitions.append(status_definitions[bit_position])
        
        return definitions
    
    def get_ch1_status(self):
        in_data = self.get_ch_status(1)
        data_processing = self.get_status_definition(in_data)
        out_data = f"{data_processing}"
        return out_data 

    def get_ch2_status(self):
        in_data = self.get_ch_status(2)
        data_processing = self.get_status_definition(in_data)
        out_data = f"{data_processing}"
        return out_data
    
    def get_ch3_status(self):
        in_data = self.get_ch_status(3)
        data_processing = self.get_status_definition(in_data)
        out_data = f"{data_processing}"
        return out_data

    # LASER STATUS
    
    def get_ch_light_state(self, channel):
        response = self.send_command(f'GET CH {channel}')
        if response and response.startswith('A CH'):
            return response.split()[2]  # Extract the light state (1 = ON; 0 = OFF)
        else:
            return "Unknown"
        
    def get_ch1_light_state(self):
        return self.get_ch_light_state(1)

    def get_ch2_light_state(self):
        return self.get_ch_light_state(2)

    def get_ch3_light_state(self):
        return self.get_ch_light_state(3)
    
    # LASER ACTIVITY
    
    def set_ch_light_state(self, channel, state):
        # `state` should be 1 for ON and 0 for OFF
        response = self.send_command(f'SET CH {channel} {state}')
        if response and response.startswith('A CH'):
            return "Success"
        else:
            return "Failed"
        
    # GET POWER READ

    def get_ch_power_measurement(self, channel):
        response = self.send_command(f'GET CHPWRWATTS {channel}')
        if response and response.startswith('A CHPWRWATTS'):
            return float(response.split()[2])  # Extract the power measurement value
        else:
            return "Unknown"
        
    def get_ch1_pw(self):
        return self.get_ch_power_measurement(1)
    
    def get_ch2_pw(self):
        return self.get_ch_power_measurement(2)
    
    def get_ch3_pw(self):
        return self.get_ch_power_measurement(3)
    
    # SET POWER LEVEL

    def set_ch_power_reference(self, channel, power):
        response = self.send_command(f'SET PWRREF {channel} {power}')
        if response and response.startswith('A PWRREF'):
            return "Success"
        else:
            return "Failed"
        
    # FAILURE CODE

    def get_ch_failure(self, channel):
        ch_failure = self.send_command(f'GET FAULT {channel}')
        if ch_failure and ch_failure.startswith('A FAULT'):
            return ch_failure.split()[2] # Extract status code
        else:
            return "Unknown"
        
    def get_failure_definition(self, binary_code):
        status_definitions = { #Redundant
            0: "Base Plate Temp. Fault",
            1: "Diode Temp. Fault",
            2: "Over Current",
            3: "Over Power",
        }
        # Ensure the binary code is 8 bits long
        binary_code = binary_code.zfill(8)
        fdefinitions = []

        # Loop through each bit in the binary code
        for bit_position, bit_value in enumerate(reversed(binary_code)):
            if bit_value == '1':
                if bit_position in status_definitions:
                    fdefinitions.append(status_definitions[bit_position])
        
        return fdefinitions
    
    def get_ch1_failure(self):
        in_data = self.get_ch_failure(1)
        data_processing = self.get_failure_definition(in_data)
        out_data = f"{data_processing}"
        return out_data

    def get_ch2_failure(self):
        in_data = self.get_ch_failure(2)
        data_processing = self.get_failure_definition(in_data)
        out_data = f"{data_processing}"
        return out_data

    def get_ch3_failure(self):
        in_data = self.get_ch_failure(3)
        data_processing = self.get_failure_definition(in_data)
        out_data = f"{data_processing}"
        return out_data