import numpy as np
import threading
import concurrency_tools as ct

from scipy.signal import find_peaks, peak_widths
from scipy.integrate import simpson
from scipy.stats import gaussian_kde

from websocket_client import WebSocketClient
from http_client import set_fpga_register, get_file
import time

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
    NUM_CHANNELS = 2
    SAMPLING_INTERVAL = 0.02  # time units in ms
    SIGNAL_DURATION = 50
    BASELINE = 0.01
    DROP_INTERVAL = 1
    DROP_WIDTH = 0.2
    DROP_CV = 0.2
    BASELINE_CV = 0.01
    MIN_WIDTH = 0.1
    MAX_WIDTH = 1

    """ Initialization """

    def __init__(self,num_channels=NUM_CHANNELS):
        self.data = {"pmt1": {"x": [0], "y": [0]}, "pmt2": {"x": [0], "y": [0]}}
        self.data2d = {"x": [0], "y": [0], "density": [0]}
        self._generate = False
        self.gain = [20, 20]
        self.thresh = 0.03
        self.gate_val = {"x0": [0], "y0": [0], "x1": [0], "y1": [0]}

        self.ws_client = WebSocketClient() 
        self.ws_client.start()  # Inicia el cliente WebSocket en un hilo

        self.vars_from_ws = variables_from_ws
        self.set_fpga_register_value("signal_duration", 50, 0, 1)
        enabled_channels = 2**num_channels - 1
        self.set_fpga_register_value("enabled_channels", enabled_channels, 0, 1)

        self.results = {
            "channel": [],
            "auc": [],
        }

    """ Start, Stop, Continue Methods to Run in the Background """

    def start_acquisition(self):
        self._generate = True
        self._thread = threading.Thread(target=self._continue_acquisition)
        self._thread.start()

    def stop_acquisition(self):
        self._generate = False

        if hasattr(self, "_thread"):
            self._thread.join()

    def _continue_acquisition(self):
        while True:
            if not self._generate:
                return
            self._acquire_signal()
            time.sleep(0.1)

    """ Generate Test PMT Signals """

    def _acquire_signal(
        self,
        num_channels=NUM_CHANNELS,
    ):  

        if self.ws_client.data_received:

            # 1D plot
            t = np.arange(0,self.ws_client.data_received["signal_duration"],self.ws_client.data_received["signal_duration"]/len(self.ws_client.data_received["voltage_history"]["voltage_history_1"]))
            for channel_idx in range(1, num_channels + 1):
                signal = np.array(self.ws_client.data_received["voltage_history"][f"voltage_history_{channel_idx}"])
                signal = signal #* self.gain[channel_idx - 1]
                self.data[f"pmt{channel_idx}"] = {"x": t, "y": signal}

            # 2D plot
            for channel in range(1, num_channels+1):
                auc = self.ws_client.data_received["cur_droplet_area"][channel-1]
                self.results["channel"].append(channel)
                self.results["auc"].append(auc * 1e6)

            # Calculate density measurement for the density scatter plot
            auc_1 = [
                self.results["auc"][i]
                for i, channel_value in enumerate(self.results["channel"])
                if channel_value == 1
            ]
            auc_2 = [
                self.results["auc"][i]
                for i, channel_value in enumerate(self.results["channel"])
                if channel_value == 2
            ]

            # Locate auc values that are zero and give them a negligible, non-zero value
            auc_1 = [x if x > 0 else 0.001 for x in auc_1]
            auc_2 = [x if x > 0 else 0.001 for x in auc_2]

            if np.size(auc_1) > 2:
                xy = np.vstack([np.log(auc_1), np.log(auc_2)])
                xy += np.random.normal(0, 1e-6, xy.shape)
                density = gaussian_kde(xy)(xy)
                self.data2d = {"x": auc_1, "y": auc_2, "density": density}

    """ Set/Update hardware values based on UI callbacks """

    def set_gain(self, value, channel=1):
        self.gain[channel - 1] = value

    def set_thresh(self, id, value):
        self.set_fpga_register_value("min_intensity_thresh", value, 0, 0, addr=id-1)
        self.thresh = value

    def set_gate_values(self, values):
        self.gate_val = values
        print(f"Gate values set {self.gate_val}")

    def set_fpga_register_value(self, var_name, value, signed, integer, addr=0):
        if isinstance(variables_to_modify[var_name],list):
            data_to_send = {"offset": variables_to_modify[var_name][addr], "value": value, "signed": signed, "integer": integer}
        else:
            print(value)
            data_to_send = {"offset": variables_to_modify[var_name], "value": value, "signed": signed, "integer": integer}
        set_fpga_register(data_to_send)

    def update_from_fpga_registers(self, var_name):
        register_value = self.ws_client.data_received[var_name]
        return register_value
    
    def get_file_history(self):
        get_file()
