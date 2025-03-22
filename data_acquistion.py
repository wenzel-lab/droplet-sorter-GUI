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
    NUM_CHANNELS = 1
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

    def __init__(self):
        self.data = {"pmt1": {"x": [0], "y": [0]}, "pmt2": {"x": [0], "y": [0]}}
        self.data2d = {"x": [0], "y": [0], "density": [0]}
        self._generate = False
        self.gain = [20, 20]
        self.thresh = 0.03
        self.gate_val = {"x0": [0], "y0": [0], "x1": [0], "y1": [0]}

        self.ws_client = WebSocketClient() 
        self.ws_client.start()  # Inicia el cliente WebSocket en un hilo

        # self.all_data = {
        #     "timestamp": 1018633.0,
        #     "droplet_id": 419,
        #     "all_data": {
        #         "min_intensity_thresh": [16209, 16209, 16209, 16209, 16209, 16209],
        #         "low_intensity_thresh": [16234, 16234, 16234, 16234, 16234, 16234],
        #         "high_intensity_thresh": [900, 900, 900, 900, 900, 900],
        #         "min_width_thresh": [1, 1, 1, 1, 1, 1],
        #         "low_width_thresh": [255, 255, 255, 255, 255, 255],
        #         "high_width_thresh": [3437096703, 3437096703, 3437096703, 3437096703, 3437096703, 3437096703],
        #         "min_area_thresh": [1, 1, 1, 1, 1, 1],
        #         "low_area_thresh": [255, 255, 255, 255, 255, 255],
        #         "high_area_thresh": [0, 0, 0, 0, 0, 0],
        #         "fads_reset": 0,
        #         "sort_delay": 100,
        #         "sort_duration": 50,
        #         "droplet_id": 419,
        #         "cur_droplet_intensity": 1,
        #         "cur_droplet_width": 1,
        #         "droplet_classification": 265,
        #         "enabled_channels": 3,
        #         "droplet_sensing_addr": 0,
        #         "raw_voltage": 16336
        #     },
        #     "voltage_history": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # }

        self.vars_from_ws = variables_from_ws
        self.set_fpga_register_value("signal_duration", 50)
        self.set_fpga_register_value("enabled_channels", 1)

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
            #self._analyze_drops()
            time.sleep(0.1)

    """ Generate Test PMT Signals """

    def _acquire_signal(
        self,
        num_channels=NUM_CHANNELS,
    ):  

        # Updating the voltages
        # if self.ws_client.data_received is None:
        #     print("No data received yet.")

        # return

        # voltage_history = self.ws_client.data_received.get("voltage_history")
        # if voltage_history is None:
        #     print("No voltage history available.")

        if self.ws_client.data_received:
            t = np.arange(0,self.ws_client.data_received["all_data"]["signal_duration"],self.ws_client.data_received["all_data"]["signal_duration"]/len(self.ws_client.data_received["voltage_history"]["voltage_history_1"]))

            for channel_idx in range(1, num_channels + 1):
                signal = np.array(self.ws_client.data_received["voltage_history"][f"voltage_history_{channel_idx}"])
                signal = signal * self.gain[channel_idx - 1]
                #for i in signal:
                #    if i != 0:
                #        print(signal)
                self.data[f"pmt{channel_idx}"] = {"x": t, "y": signal}

    """ Analyze Drop Parameters from PMT Signals """

    # def _analyze_drops(
    #     self,
    #     num_channels=NUM_CHANNELS,
    #     detection_channel=1,
    #     sampling_interval=SAMPLING_INTERVAL,
    #     min_width=MIN_WIDTH,
    #     max_width=MAX_WIDTH,
    # ):
    #     # Find drops based on the signal and threshold of the specified channel
    #     detection_signal = self.data[f"pmt{detection_channel}"]["y"]
    #     drops, _ = find_peaks(detection_signal, height=self.thresh)

    #     """
        
    #     auc_1 = self.update_from_fpga_registers("cur_droplet_intensity")
    #     droplet_sensing_address = self.update_from_fpga_registers("droplet_sensing_addr")
    #     min_area_thresh = self.update_from_fpga_registers("min_area_thresh")
    #     print(auc_1)
    #     print(droplet_sensing_address)
    #     print(min_area_thresh)

    #     self.set_fpga_register_value("min_area_thresh", 5, 0)

    #     """
        

    #     if np.any(drops) == False:
    #         # print('No peaks detected in reference channel')
    #         pass

    #     else:
    #         # Calculate widths (fwhm) of the peaks to define the time range for each drop
    #         widths, _, left_ips, right_ips = peak_widths(
    #             detection_signal, drops, rel_height=0.5
    #         )
    #         drop_widths = widths * sampling_interval  # Convert widths to time units

    #         # Filter drops based on width constraints
    #         valid_drop_indices = np.where(
    #             (drop_widths >= min_width) & (drop_widths <= max_width)
    #         )[0]
    #         valid_left_ips = left_ips[valid_drop_indices]
    #         valid_right_ips = right_ips[valid_drop_indices]
    #         valid_drop_widths = drop_widths[valid_drop_indices]

    #         # Prepare to exclude signal within drop time ranges from baseline calculation
    #         excluded_indices = np.array([], dtype=int)
    #         for left, right in zip(left_ips, right_ips):
    #             excluded_indices = np.concatenate(
    #                 (excluded_indices, np.arange(int(left), int(right)))
    #             )

    #         if np.any(valid_drop_indices) == False:
    #             print('Drops failed validity tests')
            
    #         else:

    #             # Initialize a dictionary to store the results
    #             results = {
    #                 "channel": [],
    #                 "id": [],
    #                 "timestamp": [],
    #                 "width": [],
    #                 "max signal": [],
    #                 "auc": [],
    #                 "fwhm": [],
    #                 "baseline": [],
    #             }

    #             # Initialize dictionary for baseline signals
    #             baseline_signals = {}

    #             # For each valid drop, calculate parameters
    #             for i, (left, right, width) in enumerate(
    #                 zip(valid_left_ips, valid_right_ips, valid_drop_widths), start=1
    #             ):
    #                 for channel in range(1, num_channels + 1):
    #                     # Specify the signal from a given channel
    #                     channel_signal = self.data[f"pmt{channel}"]["y"]

    #                     # Isolate baseline signal by excluding drop indices - technically don't need to calculate this for every drop
    #                     baseline_indices = np.setdiff1d(
    #                         np.arange(len(channel_signal)), excluded_indices
    #                     )
    #                     baseline_signals[channel] = np.median(
    #                         channel_signal[baseline_indices]
    #                     )
    #                     baseline = np.mean(baseline_signals[channel])

    #                     # Isolate drop signal
    #                     drop_signal = channel_signal[int(left) : int(right)]

    #                     # Calculate drop parameters
    #                     max_signal = drop_signal.max()
    #                     drop_time = self.data[f"pmt{channel}"]["x"][int(left)]
    #                     auc = simpson(drop_signal, dx=sampling_interval)
    #                     fwhm = width
    #                     drop_width = (right - left) * sampling_interval

    #                     # Append drop parameter dictionary
    #                     results["channel"].append(channel)
    #                     results["id"].append(i)
    #                     results["timestamp"].append(drop_time)
    #                     results["width"].append(drop_width)
    #                     results["max signal"].append(max_signal)
    #                     results["auc"].append(auc * 1e6)
    #                     results["fwhm"].append(fwhm)
    #                     results["baseline"].append(baseline)

    #             # Calculate density measurement for the density scatter plot
    #             auc_1 = [
    #                 results["auc"][i]
    #                 for i, channel_value in enumerate(results["channel"])
    #                 if channel_value == 1
    #             ]
    #             auc_2 = [
    #                 results["auc"][i]
    #                 for i, channel_value in enumerate(results["channel"])
    #                 if channel_value == 2
    #             ]

    #             # Locate auc values that are zero and give them a negligible, non-zero value
    #             auc_1 = [x if x > 0 else 0.001 for x in auc_1]
    #             auc_2 = [x if x > 0 else 0.001 for x in auc_2]

    #             if np.size(auc_1) > 2:
    #                 xy = np.vstack([np.log(auc_1), np.log(auc_2)])
    #                 density = gaussian_kde(xy)(xy)
    #                 self.data2d = {"x": auc_1, "y": auc_2, "density": density}

    """ Set/Update hardware values based on UI callbacks """

    def set_gain(self, value, channel=1):
        self.gain[channel - 1] = value

    def set_thresh(self, value):
        self.thresh = value

    def set_gate_values(self, values):
        self.gate_val = values
        print(f"Gate values set {self.gate_val}")

    def set_fpga_register_value(self, var_name, value, addr=0):
        if isinstance(variables_to_modify[var_name],list):
            data_to_send = {"offset": variables_to_modify[var_name][addr], "value": value}
        else:
            data_to_send = {"offset": variables_to_modify[var_name], "value": value}
        set_fpga_register(data_to_send)

    def update_from_fpga_registers(self, var_name):
        # Updating the parameters and other variables of interest
        # if isinstance(self.vars_from_ws[var_name],list):
        #     sensing_addr = self.ws_client.data_received["all_data"]["droplet_sensing_addr"]
        #     register_value = self.ws_client.data_received["all_data"][var_name][sensing_addr]
        # else:
        register_value = self.ws_client.data_received["all_data"][var_name]
        #register_value = self.all_data["all_data"][var_name]
        return register_value
    
    def get_file_history(self):
        get_file()
