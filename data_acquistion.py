import numpy as np
import threading
import concurrency_tools as ct

from scipy.signal import find_peaks, peak_widths
from scipy.integrate import simpson
from scipy.stats import gaussian_kde

from websocket_client import WebSocketClient
from http_client import set_fpga_register, set_gain, get_file
import time

# Variables received from WebSocket Server (Red Pitaya)
variables_from_ws = {
    "min_intensity_thresh": [], # x6
    "low_intensity_thresh": [], # x6
    "high_intensity_thresh": [], # x6
    "min_width_thresh": [], # x6
    "low_width_thresh": [], # x6
    "high_width_thresh": [], # x6
    "min_area_thresh": [], # x6
    "low_area_thresh": [], # x6
    "high_area_thresh": [], # x6
    "fads_reset": 0,
    "sort_delay": 0,
    "sort_duration": 0,
    "signal_duration": 0,
    "droplet_id": 0,
    "cur_droplet_intensity": [], # x6
    "cur_droplet_width": [], # x6
    "cur_droplet_area": [], # x6
    "cur_time_us": 0,
    "droplet_classification": 0,
    "enabled_channels": 0,
    "droplet_sensing_addr": 0,
    "raw_voltage": 0,
    "adc_values": [], # x6
    "update_cycle": 0,
    "cur_adc_data": [] #x6
}

# FPGA register addresses for write operations
variables_to_modify = {
    "min_intensity_thresh": ["0x01000", "0x01004", "0x01008", "0x0100c", "0x01010", "0x01014"],
    "low_intensity_thresh": ["0x01020", "0x01024", "0x01028", "0x0102c", "0x01030", "0x01034"],
    "high_intensity_thresh": ["0x01040", "0x01044", "0x01048", "0x0104c", "0x01050", "0x01054"],
    "min_width_thresh": ["0x01060", "0x01064", "0x01068", "0x0106c", "0x01070", "0x01074"],
    "low_width_thresh": ["0x01080", "0x01084", "0x01088", "0x0108c", "0x01090", "0x01094"],
    "high_width_thresh": ["0x010a0", "0x010a4", "0x010a8", "0x010ac", "0x010b0", "0x010b4"],
    "min_area_thresh": ["0x010c0", "0x010c4", "0x010c8", "0x010cc", "0x010d0", "0x010d4"],
    "low_area_thresh": ["0x010e0", "0x010e4", "0x010e8", "0x010ec", "0x010f0", "0x010f4"],
    "high_area_thresh": ["0x01100", "0x01104", "0x01108", "0x0110c", "0x01110", "0x01114"],
    "fads_reset": "0x20",
    "sort_delay": "0x24",
    "sort_duration": "0x28",
    "signal_duration": "0x100",
    "enabled_channels": "0x0300",
    "droplet_sensing_addr": "0x0304"
}

class DataAcquisition:
    """"
    Class responsible for acquiring, processing, and analyzing PMT signals
    in a droplet-based microfluidic classification system. It interfaces with a WebSocket client
    to receive streaming data and updates FPGA parameters via HTTP.

    Attributes:
        data: Dictionary containing time (x) and voltage (y) values for each PMT channel.
        data2d: Dictionary containing 2D data (x, y, and density) for scatter plots.
        ws_client: Instance of WebSocketClient that fetches data from Red Pitaya.
    """

    NUM_CHANNELS = 6
    SAMPLING_INTERVAL = 0.02  # ms
    SIGNAL_DURATION = 50
    BASELINE = 0.01
    DROP_INTERVAL = 1
    DROP_WIDTH = 0.2
    DROP_CV = 0.2
    BASELINE_CV = 0.01
    MIN_WIDTH = 0.1
    MAX_WIDTH = 1

    def __init__(self,num_channels=NUM_CHANNELS):
        """Initializes buffers, WebSocket connection, and sets default FPGA values"""

        self.data = {"pmt1": {"x": [0], "y": [0]}, "pmt2": {"x": [0], "y": [0]}, 
                     "pmt3": {"x": [0], "y": [0]}, "pmt4": {"x": [0], "y": [0]}, 
                     "pmt5": {"x": [0], "y": [0]}, "pmt6": {"x": [0], "y": [0]}}
        self.data2d = {"x": [0], "y": [0], "density": [0]}
        self.data2d_x = [1,"AUC"]
        self.data2d_y = [2,"AUC"]
        self._generate = False
        self.gain = [20, 20]
        self.thresh = 0.03
        self.gate_val = {"x0": [0], "y0": [0], "x1": [0], "y1": [0]}

        self.num_channels = num_channels

        self.ws_client = WebSocketClient() 
        # Starts the websocket client in a thread
        self.ws_client.start()  

        self.vars_from_ws = variables_from_ws
        self.set_fpga_register_value("signal_duration", 50, 0)

        self.results = {
            "channel": [],
            "AUC": [],
            "Intensity": [],
            "Width": []
        }

    """ Start, Stop, Continue Methods to Run in the Background """

    def start_acquisition(self):
        """Starts the acquisition loop in a background thread"""
        self._generate = True
        self._thread = threading.Thread(target=self._continue_acquisition)
        self._thread.start()

    def stop_acquisition(self):
        """Stops the acquisition loop and joins the background thread"""
        self._generate = False

        if hasattr(self, "_thread"):
            self._thread.join()

    def _continue_acquisition(self):
        """Continuously acquires new data until stopped"""
        while True:
            if not self._generate:
                return
            self._acquire_signal()
            time.sleep(0.1)

    def _acquire_signal(
        self,
        num_channels=NUM_CHANNELS,
    ):  
        """Processes signal and extracts features if data has been received"""

        if self.ws_client.data_received:

            enabled_channels = self.update_from_fpga_registers("enabled_channels")

            # 1D plot
            for channel_idx in range(1, num_channels + 1):
                if int(enabled_channels[num_channels-channel_idx]):
                    try:
                        t = np.arange(0,self.ws_client.data_received["signal_duration"],self.ws_client.data_received["signal_duration"]/len(self.ws_client.data_received["voltage_history"][f"voltage_history_{channel_idx}"]))
                        signal = np.array(self.ws_client.data_received["voltage_history"][f"voltage_history_{channel_idx}"])
                        signal = signal #* self.gain[channel_idx - 1]
                        self.data[f"pmt{channel_idx}"] = {"x": t, "y": signal}
                    except:
                        pass
                else:
                    self.data[f"pmt{channel_idx}"] = {"x": [0], "y": [0]}

            # 2D plot
            for channel in range(1, num_channels+1):
                auc = self.ws_client.data_received["cur_droplet_area"][channel-1]
                intensity = self.ws_client.data_received["cur_droplet_intensity"][channel-1]
                width = self.ws_client.data_received["cur_droplet_width"][channel-1]
                self.results["channel"].append(channel)
                self.results["AUC"].append(auc * 1e6)
                self.results["Intensity"].append(intensity * 1e6)
                self.results["Width"].append(width * 1e6)

            XX = [
                self.results[f"{self.data2d_x[1]}"][i]
                for i, channel_value in enumerate(self.results["channel"])
                if channel_value == self.data2d_x[0]
            ]

            YY = [
                self.results[f"{self.data2d_y[1]}"][i]
                for i, channel_value in enumerate(self.results["channel"])
                if channel_value == self.data2d_y[0]
            ]

            XX = [x if x > 0 else 0.001 for x in XX]
            YY = [x if x > 0 else 0.001 for x in YY]

            if np.size(XX) > 2:
                if np.size(XX)==np.size(YY):
                    xy = np.vstack([np.log(XX), np.log(YY)])
                    xy += np.random.normal(0, 1e-6, xy.shape)
                    density = gaussian_kde(xy)(xy)
                    self.data2d = {"x": XX, "y": YY, "density": density}


    """ Set/Update hardware values based on UI callbacks """

    def set_gain(self, gains):
        """Sends gain values to the FPGA via HTTP client"""
        data_to_send = {"values": gains}
        set_gain(data_to_send)

    def set_thresh(self, id, value):
        """Converts a threshold value and updates FPGA register"""
        digital_value = int((value-(6.1e-5))/(1.22e-4))
        self.set_fpga_register_value("min_intensity_thresh", digital_value, 1, addr=id-1)
        self.thresh = value

    def set_gate_values(self, values):
        """Updates gate thresholds for a 2D parameter-based classification region"""
        self.gate_val = values
        ychannel = self.gate_val["y_channel"]
        yparam = self.gate_val["y_param"]
        xchannel = self.gate_val["x_channel"]
        xparam = self.gate_val["x_param"]
        Ymin = self.gate_val["y0"][0]/(1e6)
        Ymax = self.gate_val["y1"][0]/(1e6)
        Xmin = self.gate_val["x0"][0]/(1e6)
        Xmax = self.gate_val["x1"][0]/(1e6)

        if yparam=="AUC":
            digital_min_thresh = int((Ymin-(6.1e-5))/(1.22e-4))
            digital_max_thresh = int((Ymax-(6.1e-5))/(1.22e-4))
            self.set_fpga_register_value("low_area_thresh", digital_min_thresh, 1, ychannel-1)
            self.set_fpga_register_value("high_area_thresh", digital_max_thresh, 1, ychannel-1)
        elif yparam=="Intensity":
            digital_min_thresh = int((Ymin-(6.1e-5))/(1.22e-4))
            digital_max_thresh = int((Ymax-(6.1e-5))/(1.22e-4))
            self.set_fpga_register_value("low_intensity_thresh", digital_min_thresh, 1, ychannel-1)
            self.set_fpga_register_value("high_intensity_thresh", digital_max_thresh, 1, ychannel-1)
        elif yparam=="Width":
            self.set_fpga_register_value("low_width_thresh", int(Ymin), 0, ychannel-1)
            self.set_fpga_register_value("high_width_thresh", int(Ymax), 0, ychannel-1)

        if xparam=="AUC":
            digital_min_thresh = int((Xmin-(6.1e-5))/(1.22e-4))
            digital_max_thresh = int((Xmax-(6.1e-5))/(1.22e-4))
            self.set_fpga_register_value("low_area_thresh", digital_min_thresh, 1, xchannel-1)
            self.set_fpga_register_value("high_area_thresh", digital_max_thresh, 1, xchannel-1)
        elif xparam=="Intensity":
            digital_min_thresh = int((Xmin-(6.1e-5))/(1.22e-4))
            digital_max_thresh = int((Xmax-(6.1e-5))/(1.22e-4))
            self.set_fpga_register_value("low_intensity_thresh", digital_min_thresh, 1, xchannel-1)
            self.set_fpga_register_value("high_intensity_thresh", digital_max_thresh, 1, xchannel-1)
        elif xparam=="Width":
            self.set_fpga_register_value("low_width_thresh", int(Xmin), 0, xchannel-1)
            self.set_fpga_register_value("high_width_thresh", int(Xmax), 0, xchannel-1)

        print(f"Gate values set {self.gate_val}")

    def set_fpga_register_value(self, var_name, value, signed, addr=0):
        """Writes a value to an FPGA register via HTTP"""
        if isinstance(variables_to_modify[var_name],list):
            data_to_send = {"offset": variables_to_modify[var_name][addr], "value": value, "signed": signed}
            print(data_to_send)
        else:
            data_to_send = {"offset": variables_to_modify[var_name], "value": value, "signed": signed}
        set_fpga_register(data_to_send)

    def update_from_fpga_registers(self, var_name):
        """Returns the latest value received from a specific FPGA register"""
        register_value = self.ws_client.data_received[var_name]
        return register_value
    
    def get_file_history(self):
        """Downloads the current history file from the FPGA system"""
        get_file()
