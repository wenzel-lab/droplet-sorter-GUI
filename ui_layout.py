import os #LibreHub
import numpy as np
import threading
import concurrency_tools as ct
import time
import math
import pandas as pd # LibreHub
import json # LibreHub
from tkinter import Tk, filedialog #LibreHub
from data_generator import DataGenerator
from test_laser import SerialManager #LibreHub
from timer import ResettableTimer #LibreHub

from bokeh.layouts import column, row
from bokeh.models import (
    ColumnDataSource,
    Slider,
    Toggle,
    Span,
    LinearColorMapper,
    Spinner,
    Div,
    Button,     #LibreHub
    TextInput,  #LibreHub
    Select,   #LibreHub
    LogTicker, #LibreHub
   )
from bokeh.models.callbacks import CustomJS
from bokeh.plotting import curdoc, figure
from bokeh.events import SelectionGeometry


class UI:
    """Initialization Methods"""

    def __init__(self):
        print("UI init")
        self._init_hardware()
        self._init_COM()
        self._init_ui()

    def _init_hardware(self):
        # Create an instance of the hardware class that will run in a separate process.
        self.dg = ct.ObjectInSubprocess(DataGenerator)
        self.dg_lock = threading.Lock()

    def _init_COM(self): # There is a hint in the SQUID script, main or setup I think where it shows how to enable COM ports. LibreHub
        self.serial_manager = SerialManager("/dev/ttyUSB0") #ttyUSB0, fix permissions

    def _init_ui(self):
        # Initialize UI components
        with self.dg_lock:
            self.doc = curdoc()
            self.timers = np.zeros(100)
            self._setup_data_sources()
            self._setup_ui_components()
            self.doc.add_periodic_callback(self.update_ui, 150)  # update ui every 150ms

    """ Datasource Setup Methods """

    def _setup_data_sources(self):
        # Initialize data sources for the generated data
        self.source_PMT1 = ColumnDataSource(
            data=self.dg.data["pmt1"]
        )  # convert from s to ms
        self.source_PMT2 = ColumnDataSource(data=self.dg.data["pmt2"])
        self.source_2d = ColumnDataSource(data=self.dg.data2d)
        self.rolling_source_2d = self.dg.data2d.copy()

        # Initialize data sources for the interactive callbacks
        self.thresh = 0.05
        self.buffer_length = 5000
        self.boxselect = {"x0": [0], "y0": [0], "x1": [0], "y1": [0]}
        self.source_bx = ColumnDataSource(data=self.boxselect)
        self.add_counter = 0 #LibreHub
        self.no_update = 0 #LibreHub
        self.timer = None #LibreHub
        self.delay = 1.0  # Debounce delay in seconds.LibreHub
        self.sub_plots_dic = {} #LibreHub
        self.sub_source_bx_dic = {} #LibreHub
        self.sub_plots_source = {} #LibreHub
        self.sub_boxselect = {"x0": [0], "y0": [0], "x1": [0], "y1": [0]} #LibreHub
        self.div_box_reset = 0 #LibreHub

    """ UI Setup Methods """

    def _setup_ui_components(self):
        # Setup update rate label, toggle, sliders, plot, and scatter plot
        self.dynamic_widgets_container = row() #LibreHub
        # FADS widgets.
        self.toggle = self._create_GATE_toggle()
        self.sliders = self._create_sliders()
        self.bufferspinner = self._create_bufferspinner()
        self.custom_div = self._create_custom_div()
        self.plot = self._create_signal_plot()
        self.plot2d = self._create_2d_scatter_plot()
        self.create_graph = self._create_GATE_new_plot() #LibreHub
        self.delete_graph = self._create_GATE_delete_plot() #LibreHub
        self.save_fads_button = self._create_FADS_EXPORT_save() #LibreHub
        self.save_logs_button = self._create_logs_EXPORT_save() #LibreHub
        self.reset_button = self._create_GATE_reset() #LibreHub
        self.layout_headers = self._create_layout_titles() #LibreHub
        self.dropdown_menu = self._create_GATE_dropdown() #LibreHub
        self.GATE_data_points = self._create_custom_GATE_1() #LibreHub
        self.DETECTOR_dropdown = self._create_DETECTOR_dropdown() #LibreHub
        self.DETECTOR_rec_button = self. _create_DETECTOR_button() #LibreHub
        self.SORTING_test_boxes = self._create_SORTING_layout() #LibreHub
        self.SORTING_slider = self._create_SORTING_slider() #LibreHub
        self.SORTING_switch = self._create_SORTING_button() #LibreHub

        # Laser widgets, LibreHub
        self.COM_ini = self._create_start_COM_toggle()
        self.COM_log_console = self._create_custom_COM_1()
        self.COM_status_error = self._create_custom_COM_2()
        self.COM_signal = self._create_custom_COM_3()
        self.LASER_1_status = self._create_call_LASER_1_status()
        self.LASER_2_status = self._create_call_LASER_2_status()
        self.LASER_3_status = self._create_call_LASER_3_status()
        self.LASER_status_code = self._create_custom_COM_status()
        self.LASER_live = self._create_custom_power_tracker()
        self.LASER_slider = self._create_laser_sliders()
        self.LASER_power = self._create_pw_input_box()

        # Generate Layout
        self.doc.add_root(
            column(
                self.layout_headers[0], #LibreHub
                self.COM_ini, #LibreHub
                row( #LibreHub
                    column(
                        row(
                            self.LASER_1_status,
                            self.LASER_live[0],
                            self.LASER_slider[0],
                            self.LASER_power[0],
                        ),
                        self.LASER_status_code[0],
                        row(
                            self.LASER_2_status,
                            self.LASER_live[1],
                            self.LASER_slider[1],
                            self.LASER_power[1],
                        ),
                        self.LASER_status_code[1],
                        row(
                            self.LASER_3_status,
                            self.LASER_live[2],
                            self.LASER_slider[2],
                            self.LASER_power[2],
                        ),
                        self.LASER_status_code[2],
                    ),
                    column(
                        self.COM_log_console,
                        row(
                            self.COM_signal,
                            self.COM_status_error,
                        ),
                    ),
                ),
                self.layout_headers[1],#LibreHub
                self.layout_headers[2],#LibreHub
                row(
                    column(
                        self.toggle,
                        self.reset_button, #LibreHub
                        row(
                            self.create_graph, #LibreHub
                            self.delete_graph, #LibrehUB
                        ),
                        self.bufferspinner, 
                        self.GATE_data_points, #LibreHub
                    ),
                    column(
                        self.custom_div,
                        self.plot2d,
                    ),
                    column(
                        self.dropdown_menu[0], #LibreHub
                        self.dropdown_menu[1], #LibreHub
                        self.dropdown_menu[2], #LibreHub
                        self.dropdown_menu[3], #LibreHub
                    ),
                    self.dynamic_widgets_container, #LibreHub
                ),
                self.layout_headers[3],#LibreHub
                column(
                    self.DETECTOR_dropdown, #LibreHub
                    self.plot,
                    self.DETECTOR_rec_button, #LibreHub
                    row(
                        column(
                            self.sliders[0],
                            self.sliders[1],
                            self.sliders[2], #LibreHub
                        ),
                        column(
                            self.sliders[3],
                            self.sliders[4], #LibreHub
                            self.sliders[5], #LibreHub
                        ),
                        
                    ),
                ),
                self.layout_headers[4],#LibreHub
                column( #LibreHub
                    row(
                        self.SORTING_test_boxes[0],
                        self.SORTING_test_boxes[1],
                        self.SORTING_test_boxes[2],
                        self.SORTING_dead_slider,
                    ),
                    row(
                        self.SORTING_test_boxes[3],
                        self.SORTING_test_boxes[4],
                        self.SORTING_test_boxes[5],
                        self.SORTING_button,
                    ),
                ),
                self.layout_headers[5],#LibreHub
                row(
                    self.save_fads_button, #LibreHub
                    self.save_logs_button, #LibreHub
                ),
                
            )
        )

    """ UI Component Methods """

    def _create_layout_titles(self): #LibreHub
        layout_titles_info = [
            {
                "text": """<span style="font-weight: bold; font-size: 20px; text-decoration: underline;">Laser Module</span>""",
                "width": 400,
                "height": 30,
            },
            {
                "text": """<span style="font-weight: bold; font-size: 20px; text-decoration: underline;">FADS Module</span>""",
                "width": 400,
                "height": 30,
            },
            {
                "text": """<span style="font-size: 16px; text-decoration: underline;">Gating</span>""",
                "width": 400,
                "height": 30,
            },
            {
                "text": """<span style="font-size: 16px; text-decoration: underline;">Detector Settings</span>""",
                "width": 400,
                "height": 30,
            },
            {
                "text": """<span style="font-size: 16px; text-decoration: underline;">Sorting</span>""",
                "width": 400,
                "height": 30,
            },
            {
                "text": """<span style="font-weight: bold; font-size: 20px; text-decoration: underline;">Save Data</span>""",
                "width": 400,
                "height": 30,
            },
        ]

        self.layout_titles =[]
        for layout_title_info in layout_titles_info:
            self.custom_div_title = Div(
                text=layout_title_info["text"],
                width=layout_title_info["width"],
                height=layout_title_info["height"],
            )
            self.layout_titles.append(self.custom_div_title)
        return self.layout_titles

    def _create_start_COM_toggle(self): #LibreHub
        self.init_COM_toggle = Button(
            label="Connect",
            button_type="primary",
            )
        self.init_COM_toggle.on_click(self.initialize_serial_toggle)

        return self.init_COM_toggle
    
    def _create_custom_COM_1(self): #LibreHub
        self.custom_COM_1 = Div(
            text = "",
            width = 307,
            height = 200,
            styles = {"overflow-y":"scroll", "background-color":"lightgray","border-radius":"10px","padding":"10px"},
            visible = False,
            margin = [45,0,0,80],
        )
        return self.custom_COM_1
    
    def _create_custom_COM_2(self): #LibreHub
        self.custom_COM_2 = TextInput(
            value = "No Data",
            visible = False,
            resizable = "width",
            margin = [19,0,0,20],
            disabled = True,
            )

        return self.custom_COM_2

    def _create_custom_COM_3(self): #LibreHub
        self.custom_COM_3 = Button(
            label = "STATUS",
            button_type = "success",
            visible = False,
            margin = [20,0,0,80],
            )

        return self.custom_COM_3
    
    def _create_custom_COM_status(self): #LibreHub
        COM_statuses_margin = [0,0,50,62]
        COM_statuses_info = [
            {
                "text": "STATUS: No Data",
                "visible": False,
                "resizable": "width",
                "disabled": True,
            },
            {
                "text": "STATUS: No Data",
                "visible": False,
                "resizable": "width",
                "disabled": True,
            },
            {
                "text": "STATUS: No Data",
                "visible": False,
                "resizable": "width",
                "disabled": True,
            },
        ]

        self.COM_statuses = []
        for COM_status_info in COM_statuses_info:
            self.custom_COM_status = TextInput(
                value=COM_status_info["text"],
                visible=COM_status_info["visible"],
                disabled=COM_status_info["disabled"],
                resizable = COM_status_info["resizable"],
                margin=COM_statuses_margin,
                )
            self.COM_statuses.append(self.custom_COM_status)
        return self.COM_statuses
    
    def _create_custom_power_tracker(self): #LibreHub
        power_trackers_info = [
            {
                "title": "Power [mW]",
                "value": "No Data",
                "width": 75,
                "disabled": True
            },
            {
                "title": "Power [mW]",
                "value": "No Data",
                "width": 75,
                "disabled": True
            },
            {
                "title": "Power [mW]",
                "value": "No Data",
                "width": 75,
                "disabled": True
            },
        ]
        
        self.power_trackers = []
        for power_tracker_info in power_trackers_info:
            power_tracker = TextInput(
                    title = power_tracker_info["title"],
                    value = power_tracker_info["value"],
                    width = power_tracker_info["width"],
                    disabled = power_tracker_info["disabled"]
                    )
            self.power_trackers.append(power_tracker)
        return self.power_trackers

    def _create_call_LASER_1_status(self): #LibreHub
        self.call_LASER_1_status_sign = Button(
            label="488",
            button_type="default",
            margin=[22,0,22,10]
            )
        self.call_LASER_1_status_sign.on_click(self.show_and_toggle_LASER_1_status)

        return self.call_LASER_1_status_sign

    def _create_call_LASER_2_status(self): #LibreHub
        self.call_LASER_2_status_sign = Button(
            label="638",
            button_type="default",
            margin=[22,0,22,10]
            )
        self.call_LASER_2_status_sign.on_click(self.show_and_toggle_LASER_2_status)

        return self.call_LASER_2_status_sign

    def _create_call_LASER_3_status(self): #LibreHub
        self.call_LASER_3_status_sign = Button(
            label="405",
            button_type="default",
            margin=[22,0,22,10]
            )
        self.call_LASER_3_status_sign.on_click(self.show_and_toggle_LASER_3_status)

        return self.call_LASER_3_status_sign

    def _create_laser_sliders(self): #LibreHub
        laser_slider_margin = (10, 10, 20, 20)

        laser_sliders_info = [
            {
                "start": 0.3,
                "end": 45,
                "value": 0.5,
                "step": 0.3,
                "title": "Laser 1 [mW]",
                "bar_color": "mediumseagreen",
                "orientation": "horizontal",
                "callback": self._schedule_update_slider_1,
            },
            {
                "start": 0.3,
                "end": 45,
                "value": 0.5,
                "step": 0.3,
                "title": "Laser 2 [mW]",
                "bar_color": "mediumseagreen",
                "orientation": "horizontal",
                "callback": self._schedule_update_slider_2,
            },
            {
                "start": 0.3,
                "end": 45,
                "value": 0.5,
                "step": 0.3,
                "title": "Laser 3 [mW]",
                "bar_color": "mediumseagreen",
                "orientation": "horizontal",
                "callback": self._schedule_update_slider_3,
            },
        ]

        self.laser_sliders = []
        for laser_slider_info in laser_sliders_info:
            laser_slider = Slider(
                start=laser_slider_info["start"],
                end=laser_slider_info["end"],
                value=laser_slider_info["value"],
                step=laser_slider_info["step"],
                title=laser_slider_info["title"],
                bar_color=laser_slider_info["bar_color"],
                orientation= laser_slider_info["orientation"],
                disabled = True,
                margin=laser_slider_margin,
            )
            laser_slider.on_change("value", laser_slider_info["callback"])
            self.laser_sliders.append(laser_slider)

        return self.laser_sliders
    
    def _create_pw_input_box(self): #LibreHub

        lasers_w_box = [
            {
                "title": "0-45",
                "value": "0",
                "width" : 50,
                "callback": self._set_power_box_1
            },
            {
                "title": "0-45",
                "value": "0",
                "width" : 50,
                "callback": self._set_power_box_2
            },
            {
                "title": "0-45",
                "value": "0",
                "width" : 50,
                "callback": self._set_power_box_3
            },
        ]

        self.laser_boxes = []
        for laser_w_box in lasers_w_box:
            laser_input_box = TextInput(
                title=laser_w_box["title"],
                value = laser_w_box["value"],
                width = laser_w_box["width"],
                )
            laser_input_box.on_change("value", laser_w_box["callback"])
            self.laser_boxes.append(laser_input_box)

        return self.laser_boxes
    
    def _create_GATE_new_plot(self):
        self.create_plot_button = Button(
            label = "Add",
            button_type = "success",
            margin = [20,0,20,30]
            )
         
        self.create_plot_button.on_click(self._add_widget)

        return self.create_plot_button
    
    def _create_GATE_delete_plot(self):
        self.delete_plot_button = Button(
            label = "Remove",
            button_type = "danger",
            margin = [20,0,20,20]
            )
         
        self.delete_plot_button.on_click(self._remove_widget)

        return self.delete_plot_button

    def _create_GATE_toggle(self): #LibreHub
        self.toggle = Toggle(
            label="Start Experiment",
            button_type="primary",
            margin=[160,100,20,30],
            )
        self.toggle.on_click(self._toggle_changed)

        return self.toggle
    
    def _create_GATE_dropdown(self): #LibreHub
        dropdown_boxes_info = [
            {
                "title" : "Y Channel",
                "value" : "1",
                "options" : ["1","2","3"],
                "width" : 100,
                "margin" : [140,30,20,30],
            },
            {
                "title" : "Y Parameter",
                "value" : "a",
                "options" : ["a","b","c"],
                "width" : 100,
                "margin" : [20,30,20,30],
            },
            {
                "title" : "X Channel",
                "value" : "1",
                "options" : ["1","2","3"],
                "width" : 100,
                "margin" : [20,30,20,30],
            },
            {
                "title" : "X Parameter",
                "value" : "a",
                "options" : ["a","b","c"],
                "width" : 100,
                "margin" : [20,30,20,30],
            },
        ]

        self.dropdown_boxes = []
        for dropdown_box_info in dropdown_boxes_info:
            dropdown_widget = Select(
                title = dropdown_box_info["title"],
                value = dropdown_box_info["value"],
                options = dropdown_box_info["options"],
                width = dropdown_box_info["width"],
                margin = dropdown_box_info["margin"],
                disabled = True,
            )
            #dropdown_widget.on_change("value",dropdown_box_info["callback"])
            self.dropdown_boxes.append(dropdown_widget)

        return self.dropdown_boxes
    
    def _create_custom_GATE_1(self): #LibreHub
        self.custom_GATE_1 = TextInput(
            title = "N° Data Points",
            value = "0",
            margin = [10,0,0,30],
            width = 150,
            visible = True,
            disabled = True,
        )

        return self.custom_GATE_1

    def _create_GATE_reset(self): #LibreHub
        self.reset_button = Button(
            label = "Reset Experiment",
            button_type = "warning",
            margin = [10,30,20,30]
            )
        self.reset_button.on_click(self._reset_button_clicked)

        return self.reset_button
    
    def _create_DETECTOR_dropdown(self): #LibreHub
        self.detector_selection = Select(
            title = "Detector",
            value = "All",
            options = ["All","PMT1","PMT2"],
            width = 100,
            margin = [20,0,0,420],
            disabled = False,
        )
        self.detector_selection.on_change("value",self._toggle_pmt_signal)

        return self.detector_selection
    
    def _create_DETECTOR_button(self): #LibreHub
        self.detector_record = Button(
            label = "Record 1 second",
            button_type = "primary",
            margin = [20,0,0,420],
            disabled = False,
        )
        self.detector_record.on_click(self._record_signal)

        return self.detector_record
    
    def _create_SORTING_layout(self): #LibreHub
        sorting_layout_info = [
            {
                "title" : "Frequency [kHz]",
                "value" : "123",
                "disabled" : False,
            },
            {
                "title" : "Voltage [kV]",
                "value" : "123",
                "disabled" : False,
            },
            {
                "title" : "Pulse Duration [time]",
                "value" : "123",
                "disabled" : False,
            },
            {
                "title" : "Delay [time]",
                "value" : "123",
                "disabled" : False,
            },
            {
                "title" : "Sorted Droplets",
                "value" : "123",
                "disabled" : True,
            },
            {
                "title" : "Total Events",
                "value" : "123",
                "disabled" : True,
            },
        ]
        
        self.sorting_boxes = []
        for sorting_info in sorting_layout_info:
            custom_sorting_box = TextInput(
                title = sorting_info["title"],
                value = sorting_info["value"],
                disabled = sorting_info["disabled"],
                width = 100,
                margin = [20,20,20,20],
            )
            self.sorting_boxes.append(custom_sorting_box)

        return self.sorting_boxes
    
    def _create_SORTING_slider(self): #LibreHub
        self.SORTING_dead_slider = Slider(
            start = 0,
            end = 1,
            value = 0.5,
            step = 0.1,
            title = "Dead Time",
            bar_color = "royalblue",
            margin = [25,0,0,70],
            disabled = True,
        )

        return self.SORTING_dead_slider
    
    def _create_SORTING_button(self): #LibreHub
        self.SORTING_button = Button(
            label = "On",
            button_type = "primary",
            margin = [40,0,0,196],
            disabled = True,
        )

        return self.SORTING_button
    
    def _create_logs_EXPORT_save(self): #LibreHub
        self.save_button = Button(
            label="Save logs",
            button_type="primary",
            margin = [39,0,0,20],
            )
        self.save_button.on_click(self._save_button_clicked_1)
        
        return self.save_button

    def _create_FADS_EXPORT_save(self): #LibreHub
        self.save_button = Button(
            label="Save data",
            button_type="primary",
            margin = [39,0,0,20],
            )
        self.save_button.on_click(self._save_button_clicked_2)
        
        return self.save_button

    def _create_2d_scatter_sub_plot(self, data_source): #LibreHub
        color_mapper = LinearColorMapper(palette="Viridis256")
        self.sub_plot2d = figure(
            height=400,
            width=450,
            margin = [0,0,30,0],
            x_axis_label="Channel 1 AUC",
            y_axis_label="Channel 2 AUC",
            x_range=(1e3, 1e6),
            y_range=(1e3, 1e6),
            x_axis_type="log",
            y_axis_type="log",
            title=f"Density Scatter Plot {self.add_counter + 2}",
            tools="box_select,reset,wheel_zoom,box_zoom,pan",
        )
        self.glyph_sub = self.sub_plot2d.scatter(
            "x",
            "y",
            source=data_source,
            size=2,
            color={"field": "density", "transform": color_mapper},
            line_color=None,
            fill_alpha=0.6,
        )
        self.glyph_sub.nonselection_glyph = None  # supress alpha change for nonselected indices bc refresh messes this up

        return self.sub_plot2d

    def _create_signal_plot(self):
        plot_margin = (30, 0, 0, 10)
        self.plot = figure(
            height=300,
            width=900,
            title="Generated PMT Data",
            x_axis_label="Time(ms)",
            y_axis_label="Voltage",
            toolbar_location=None,
            x_range=(0, 50),
            y_range=(0, 1.2),
            margin=plot_margin,
        )
        self.line_pmt1 = self.plot.line(
            "x",
            "y",
            source=self.source_PMT1,
            color="mediumseagreen",
            legend_label="PMT1",
        )
        self.line_pmt2 = self.plot.line(
            "x",
            "y",
            source=self.source_PMT2,
            color="royalblue",
            legend_label="PMT2",
        )
        self._create_threshold_lines()

        return self.plot

    def _create_threshold_lines(self):
        self.thresh_line = Span(
            location=self.thresh,
            dimension="width",
            line_color="mediumseagreen",
            line_width=2,
            line_dash="dotted",
        )
        self.plot.add_layout(self.thresh_line)

    def _create_sliders(self):

        sliders_info = [
            {
                "start": 0.01,
                "end": 1,
                "value": 0.5,
                "step": 0.01,
                "title": "Detector 1 Gain",
                "bar_color": "mediumseagreen",
                "margin" : [20, 10, 20, 50],
                "callback": self._gain1_changed,
                "disabled" : False,
            },
            {
                "start": 0.01,
                "end": 1,
                "value": 0.5,
                "step": 0.01,
                "title": "Detector 2 Gain",
                "bar_color": "royalblue",
                "margin" : [20, 10, 20, 50],
                "callback": self._gain2_changed,
                "disabled" : False,
            },
            { #LibreHub
                "start": 0.01,
                "end": 1,
                "value": 0.5,
                "step": 0.01,
                "title": "Detector 3 Gain",
                "bar_color": "royalblue",
                "margin" : [20, 10, 20, 50],
                "callback": self._gain2_changed,
                "disabled" : True,
            },
            {
                "start": 0,
                "end": 2,
                "value": self.thresh,
                "step": 0.01,
                "title": "Noise Threshold 1",
                "bar_color": "mediumseagreen",
                "margin" : [20, 10, 20, 250],
                "callback": self._thresh_changed,
                "disabled" : False,
            },
            { #LibreHub
                "start": 0,
                "end": 2,
                "value": self.thresh,
                "step": 0.01,
                "title": "Noise Threshold 2",
                "bar_color": "mediumseagreen",
                "margin" : [20, 10, 20, 250],
                "callback": self._thresh_changed,
                "disabled" : True,
            },
            { #LibreHub
                "start": 0,
                "end": 2,
                "value": self.thresh,
                "step": 0.01,
                "title": "Noise Threshold 3",
                "bar_color": "mediumseagreen",
                "margin" : [20, 10, 20, 250],
                "callback": self._thresh_changed,
                "disabled" : True,
            },
        ]

        self.sliders = []
        for slider_info in sliders_info:
            slider = Slider(
                start=slider_info["start"],
                end=slider_info["end"],
                value=slider_info["value"],
                step=slider_info["step"],
                title=slider_info["title"],
                bar_color=slider_info["bar_color"],
                margin=slider_info["margin"],
                disabled=slider_info["disabled"],
            )
            slider.on_change("value", slider_info["callback"])
            self.sliders.append(slider)

        return self.sliders

    def _create_bufferspinner(self):
        buffer_margin = (10, 0, 20, 30)
        self.bufferspinner = Spinner(
            title="Max. Data Points Displayed",
            low=0,
            high=10000,
            step=500,
            value=self.buffer_length,
            width=150,
            margin=buffer_margin,
        )
        self.bufferspinner.on_change("value", self._spinner_changed)

        return self.bufferspinner

    def _create_divhtml(self):
        # Extracting float values from the dictionary
        float_values = [self.boxselect[key][0] for key in ["x0", "y0", "x1", "y1"]]

        if self.div_box_reset == 1:
            float_values = [0,0,0,0]

        # Convert float values to a string format of 10^x
        def to_scientific_with_superscript(value):
            if value == 0:
                return "0"
            exponent = math.floor(math.log10(abs(value)))
            base = value / 10**exponent
            return f"{base:.1f} × 10<sup>{exponent}</sup>"

        formatted_values = [
            to_scientific_with_superscript(value) for value in float_values
        ]

        # Labels for each box
        labels = [
            "X<sub>min</sub>",
            "Y<sub>min</sub>",
            "X<sub>max</sub>",
            "Y<sub>max</sub>",
        ]

        # HTML template with embedded CSS for styling
        self.html_content = f"""
        <div style="padding: 10px; background-color: white;">
            <div style="color: black; padding: 5px; background-color: white; text-align: center;"><b></b></div>
            <div style="display: flex; justify-content: space-around; padding: 5px;">
                {''.join([f'<div style="width: 80px;"><div style="text-align: center; margin-bottom: 5px;">{label}</div><div style="background-color: #E8E8E8; color: black; padding: 10px; border-radius: 10px; text-align: center; margin-right: 2px; margin-left: 2px; ">{value}</div></div>' for label, value in zip(labels, formatted_values)])}
            </div>
        </div>
        """

        self.div_box_reset = 0

        return self.html_content
    
    def _create_sub_divhtml(self): #LibreHub
        # Extracting float values from the dictionary
        float_values = [self.sub_boxselect[key][0] for key in ["x0", "y0", "x1", "y1"]]

        if self.div_box_reset == 1:
            float_values = [0,0,0,0]

        # Convert float values to a string format of 10^x
        def to_scientific_with_superscript(value):
            if value == 0:
                return "0"
            exponent = math.floor(math.log10(abs(value)))
            base = value / 10**exponent
            return f"{base:.1f} × 10<sup>{exponent}</sup>"

        formatted_values = [
            to_scientific_with_superscript(value) for value in float_values
        ]

        # Labels for each box
        labels = [
            "X<sub>min</sub>",
            "Y<sub>min</sub>",
            "X<sub>max</sub>",
            "Y<sub>max</sub>",
        ]

        # HTML template with embedded CSS for styling
        self.sub_html_content = f"""
        <div style="padding: 10px; background-color: white;">
            <div style="color: black; padding: 5px; background-color: white; text-align: center;"><b></b></div>
            <div style="display: flex; justify-content: space-around; padding: 5px;">
                {''.join([f'<div style="width: 80px;"><div style="text-align: center; margin-bottom: 5px;">{label}</div><div style="background-color: #E8E8E8; color: black; padding: 10px; border-radius: 10px; text-align: center; margin-right: 2px; margin-left: 2px; ">{value}</div></div>' for label, value in zip(labels, formatted_values)])}
            </div>
        </div>
        """

        self.div_box_reset = 0

        return self.sub_html_content

    def _create_custom_div(self):
        div_margin = (0, 0, 20, 68)

        # Creating the Bokeh Div object with the HTML content
        self.custom_div = Div(
            text=self._create_divhtml(), width=400, height=100, margin=div_margin
        )

        return self.custom_div
    
    def _create_sub_custom_div(self): #LibreHub
        div_margin = (0, 0, 20, 68)

        # Creating the Bokeh Div object with the HTML content
        self.sub_custom_div = Div(
            text=self._create_sub_divhtml(), width=400, height=100, margin=div_margin
        )

        return self.sub_custom_div

    def _create_2d_scatter_plot(self):
        color_mapper = LinearColorMapper(palette="Viridis256")
        self.plot2d = figure(
            height=400,
            width=450,
            margin = [0,0,30,0],
            x_axis_label="Channel 1 AUC",
            y_axis_label="Channel 2 AUC",
            x_range=(1e3, 1e6),
            y_range=(1e3, 1e6),
            x_axis_type="log",
            y_axis_type="log",
            title="Density Scatter Plot 1",
            tools="box_select,reset,wheel_zoom,box_zoom,pan",
        )
        self.glyph = self.plot2d.scatter(
            "x",
            "y",
            source=self.source_2d,
            size=2,
            color={"field": "density", "transform": color_mapper},
            line_color=None,
            fill_alpha=0.6,
        )
        self.glyph.nonselection_glyph = None  # supress alpha change for nonselected indices bc refresh messes this up
        self._boxselect_changed()

        return self.plot2d

    """ Callback Methods """
    def initialize_serial_toggle(self): #Something is delaying the toggle when Laser is disconnected. Delaying may come from spamming instructions from Slider, consider creating customJS. LibreHub
        with self.dg_lock:
            if self.serial_manager.serial_connection is None:
                self._update_log("> [console]: ERROR, No COM port communication.")
                self.call_LASER_1_status_sign.button_type = "warning"
                self.call_LASER_2_status_sign.button_type = "warning"
                self.call_LASER_3_status_sign.button_type = "warning"
            else:
                if self.init_COM_toggle.button_type == "primary":
                    self.init_COM_toggle.button_type = "success"
                    self._update_log("> [console]: COM communication established.")
                    self.custom_COM_1.visible = True
                    self.custom_COM_2.visible = True
                    self.custom_COM_3.visible = True
                    self.call_LASER_1_status_sign.button_type = "danger"
                    self.COM_statuses[0].visible = True
                    self.call_LASER_2_status_sign.button_type = "danger"
                    self.COM_statuses[1].visible = True
                    self.call_LASER_3_status_sign.button_type = "danger"
                    self.COM_statuses[2].visible = True
                else:
                    self.init_COM_toggle.button_type = "primary"
                    self._update_log("> [console]: COM communication disconnected.")
                    self.call_LASER_1_status_sign.button_type = "default"
                    self.serial_manager.set_ch_light_state(1,0)
                    self.call_LASER_2_status_sign.button_type = "default"
                    self.serial_manager.set_ch_light_state(2,0)
                    self.call_LASER_3_status_sign.button_type = "default"
                    self.serial_manager.set_ch_light_state(3,0)
                    self.serial_manager.set_ch_power_reference(1, 0.5)
                    self.serial_manager.set_ch_power_reference(2, 0.5)
                    self.serial_manager.set_ch_power_reference(3, 0.5)
                    self.laser_sliders[0].disabled = True
                    self.laser_sliders[1].disabled = True
                    self.laser_sliders[2].disabled = True

    def show_and_toggle_LASER_1_status(self): #LibreHub
        with self.dg_lock:
            if self.init_COM_toggle.button_type == "success":
                #Laser 1 status
                ch1_light_state = self.serial_manager.get_ch1_light_state()
                if int(ch1_light_state) == 0:
                    self.serial_manager.set_ch_light_state(1,1)
                    self.call_LASER_1_status_sign.button_type = "success"
                    self.call_LASER_1_status_sign.label = "488"
                    self._update_log("> [console]: LASER 1 ON.")
                    self.laser_sliders[0].disabled = False

                else:
                    self.serial_manager.set_ch_light_state(1,0)
                    self.call_LASER_1_status_sign.button_type = "danger"
                    self.call_LASER_1_status_sign.label = "488"
                    self._update_log("> [console]: LASER 1 OFF.")
                    self.laser_sliders[0].disabled = True
            else:
                self._update_log("> [console]: NO CONNECTION (LASER 1)")

    def show_and_toggle_LASER_2_status(self): #LibreHub
        with self.dg_lock:
            if self.init_COM_toggle.button_type == "success":
                #Laser 2 status
                ch2_light_state = self.serial_manager.get_ch2_light_state()
                if int(ch2_light_state) == 0:
                    self.serial_manager.set_ch_light_state(2,1)
                    self.call_LASER_2_status_sign.button_type = "success"
                    self.call_LASER_2_status_sign.label = "638"
                    self._update_log("> [console]: LASER 2 ON.")
                    self.laser_sliders[1].disabled = False

                else:
                    self.serial_manager.set_ch_light_state(2,0)
                    self.call_LASER_2_status_sign.button_type = "danger"
                    self.call_LASER_2_status_sign.label = "638"
                    self._update_log("> [console]: LASER 2 OFF.")
                    self.laser_sliders[1].disabled = True
            else:
                self._update_log("> [console]: NO CONNECTION (LASER 2).")

    def show_and_toggle_LASER_3_status(self): #LibreHub
        with self.dg_lock:
            if self.init_COM_toggle.button_type == "success":
                #Laser 3 status
                ch3_light_state = self.serial_manager.get_ch3_light_state()
                if int(ch3_light_state) == 0:
                    self.serial_manager.set_ch_light_state(3,1)
                    self.call_LASER_3_status_sign.button_type = "success"
                    self.call_LASER_3_status_sign.label = "405"
                    self._update_log("> [console]: LASER 3 ON.")
                    self.laser_sliders[2].disabled = False

                else:
                    self.serial_manager.set_ch_light_state(3,0)
                    self.call_LASER_3_status_sign.button_type = "danger"
                    self.call_LASER_3_status_sign.label = "405"
                    self._update_log("> [console]: LASER 3 OFF.")
                    self.laser_sliders[2].disabled = True
            else:
                self._update_log("> [console]: NO CONNECTION (LASER 3).")

    def _schedule_update_slider_1(self, attr, old, new):
        if self.timer is not None:
            self.timer.cancel()  # Cancel the previous timer if it exists
        self.timer = ResettableTimer(self.delay, self._set_slider_1_power_safe)
        self.timer.start()

    def _set_slider_1_power_safe(self):
        curdoc().add_next_tick_callback(self._set_slider_1_power)
    
    def _set_slider_1_power(self): # min 0.3 y max 45 mW. LibreHub
        with self.dg_lock:
            if self.init_COM_toggle.button_type == "success":
                try:
                    power = float(self.laser_sliders[0].value)
                    self.serial_manager.set_ch_power_reference(1, power)
                    self._update_log(f"> [console]: LASER 1 power slider set to {power} [mW].")
                except ValueError:
                    print("Invalid power value.")
            else:
                self._update_log("> [console]: NO CONNECTION (LASER_PW_SLIDER_1).")

    def _schedule_update_slider_2(self, attr, old, new):
        if self.timer is not None:
            self.timer.cancel()  # Cancel the previous timer if it exists
        self.timer = ResettableTimer(self.delay, self._set_slider_2_power_safe)
        self.timer.start()

    def _set_slider_2_power_safe(self):
        curdoc().add_next_tick_callback(self._set_slider_2_power)

    def _set_slider_2_power(self): # min 0.3 y max 45 mW. LibreHub
        with self.dg_lock:
            if self.init_COM_toggle.button_type == "success":
                try:
                    power = float(self.laser_sliders[1].value)
                    self.serial_manager.set_ch_power_reference(2, power)
                    self._update_log(f"> [console]: LASER 2 power slider set to {power} [mW].")
                except ValueError:
                    print("Invalid power value.")
            else:
                self._update_log("> [console]: NO CONNECTION (LASER_PW_SLIDER_2).")

    def _schedule_update_slider_3(self, attr, old, new):
        if self.timer is not None:
            self.timer.cancel()  # Cancel the previous timer if it exists
        self.timer = ResettableTimer(self.delay, self._set_slider_3_power_safe)
        self.timer.start()

    def _set_slider_3_power_safe(self):
        curdoc().add_next_tick_callback(self._set_slider_3_power)
    
    def _set_slider_3_power(self): # min 0.3 y max 45 mW. LibreHub
        with self.dg_lock:
            if self.init_COM_toggle.button_type == "success":
                try:
                    power = float(self.laser_sliders[2].value)
                    self.serial_manager.set_ch_power_reference(3, power)
                    self._update_log(f"> [console]: LASER 3 power slider set to {power} [mW].")
                except ValueError:
                    print("Invalid power value.")
            else:
                self._update_log("> [console]: NO CONNECTION (LASER_PW_SLIDER_3).")

    def _set_power_box_1(self, attr, old, new): # min 0.3 y max 45 mW. LibreHub    
        if self.init_COM_toggle.button_type == "success":
            try:
                power = float(self.laser_boxes[0].value)
                if 0 <= power <= 45:
                    self.serial_manager.set_ch_power_reference(1, power)
                    self._update_log(f"> [console]: LASER 1 power set to {power} [mW].")
                else:
                    self._update_log(f"> [console]: LASER 1 {power} [mW]. Power value out of range.")    
            except ValueError:
                self._update_log("> [console]: LASER 1 power value is invalid.")
        else:
            self._update_log("> [console]: NO CONNECTION (LASER_PW_1).")

    def _set_power_box_2(self, attr, old, new): # min 0.3 y max 45 mW. LibreHub    
        if self.init_COM_toggle.button_type == "success":
            try:
                power = float(self.laser_boxes[1].value)
                if 0 <= power <= 45:
                    self.serial_manager.set_ch_power_reference(2, power)
                    self._update_log(f"> [console]: LASER 2 power set to {power} [mW].")
                else:
                    self._update_log(f"> [console]: LASER 2 {power} [mW]. Power value out of range.")
            except ValueError:
                self._update_log("> [console]: LASER 2 power value is invalid.")
        else:
            self._update_log("> [console]: NO CONNECTION (LASER_PW_2).")

    def _set_power_box_3(self, attr, old, new): # min 0.3 y max 45 mW. LibreHub    
        if self.init_COM_toggle.button_type == "success":
            try:
                power = float(self.laser_boxes[2].value)
                if 0 <= power <= 45:
                    self.serial_manager.set_ch_power_reference(3, power)
                    self._update_log(f"> [console]: LASER 3 power set to {power} [mW].")
                else:
                    self._update_log(f"> [console]: LASER 3 {power} [mW]. Power value out of range.")
            except ValueError:
                self._update_log("> [console]: LASER 3 power value is invalid.")
        else:
            self._update_log("> [console]: NO CONNECTION (LASER_PW_3).")

    def _update_log(self, message): #LibreHub
        self.custom_COM_1.text += f"{message}<br>"

    def _add_widget(self): #LibreHub
        unique_id = f"plot_{self.add_counter}"
        self.sub_plots_source[unique_id] = ColumnDataSource(data={"x": [0], "y": [0], "density": [0]})
        new_sub_plot = self._create_2d_scatter_sub_plot(self.sub_plots_source[unique_id])
        self.sub_plots_dic[unique_id] = new_sub_plot
        self._sub_boxselect_changed(unique_id)
        self.add_counter += 1
        new_dropdown = self._create_GATE_dropdown()
        for i in new_dropdown:
            i.margin = [20,30,20,30]
        new_attachement = column(new_dropdown)
        self.div_box_reset = 1
        new_panel = self._create_sub_custom_div()
        self.dynamic_widgets_unit = column(new_panel, row(new_sub_plot, new_attachement))
        self.dynamic_widgets_container.children.append(self.dynamic_widgets_unit)

    def _remove_widget(self): #LibreHub
        with self.dg_lock:
            if self.dynamic_widgets_container.children:
                plot_id = f"plot_{self.add_counter - 1}"
                if plot_id in self.sub_plots_source:
                    # Clear the data source by setting all columns to empty lists
                    self.sub_plots_source[plot_id].data = {"x": [], "y": [], "density": []}
                    # Remove the data source from the dictionary
                    del self.sub_plots_source[plot_id]
                    # Remove the plot from the dictionary
                    del self.sub_plots_dic[plot_id]
                self.dynamic_widgets_container.children.pop()
                self.add_counter -= 1
        
    def _reset_button_clicked(self): #LibreHub
        #Solved with variable status self.no_update.
        with self.dg_lock:
            self.no_update = 1
            self.div_box_reset = 1
            
            self.GATE_data_points.value = "0"
            #Clean plot_0
            #Source
            for key in self.rolling_source_2d:
                self.rolling_source_2d[key] = [np.nan]
            self.source_2d.data = {key: [] for key in self.source_2d.data}
            #Coordinates
            self.custom_div.text = self._create_divhtml()

            #Clean dynamic plots
            # Source
            if self.dynamic_widgets_container.children:
                plot_keys = list(self.sub_plots_source.keys())
                for dyn_plot_source in plot_keys:
                    # Clear the data source by setting all columns to empty lists
                    self.sub_plots_source[dyn_plot_source].data = {"x": [], "y": [], "density": []}
            #Coordinates
            for p1 in range(len(self.dynamic_widgets_container.children)):
                self.div_box_reset = 1
                self.dynamic_widgets_container.children[p1].children[0].text = self._create_sub_divhtml()

    def _save_button_clicked_1(self): #LibreHub
        with self.dg_lock:
            custom_console_log = self.custom_COM_1.text
            
            # Hide the root window
            root = Tk()
            root.withdraw()

            # Prompt the user to select a save location
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            
            if file_path:
                try:
                    # Write the console log to the selected file
                    with open(file_path, "w") as f_output:
                        f_output.write(custom_console_log)
                except Exception as e:
                    print(f"An error ocurred while saving the file: {e}")
            else:
                print("No file selected.")

    def _save_button_clicked_2(self): #LibreHub
        with self.dg_lock:
            # Backup the necessary data before saving
            backup_0 = self.source_2d
            backup_1 = self.source_PMT1
            backup_2 = self.source_PMT2
            backup_3 = [self.sliders[0].value, self.sliders[1].value, self.sliders[2].value]
            backup_4 = self.bufferspinner.value
            backup_5 = [self.laser_boxes[0].value, self.laser_boxes[1].value, self.laser_boxes[2].value]
            backup_6 = [self.laser_sliders[0].value, self.laser_sliders[1].value, self.laser_sliders[2].value]
            
            # Hide the root window
            root = Tk()
            root.withdraw()

            # Prompt the user to select a save location
            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])

            if file_path:    
                # Convert the data to DataFrames and dictionaries
                df_0 = pd.DataFrame(backup_0.data)
                df_1 = pd.DataFrame(backup_1.data)
                df_2 = pd.DataFrame(backup_2.data)
                df_3 = backup_3
                df_4 = str(backup_4)
                df_5 = [backup_5[0], backup_6[0]]
                df_6 = [backup_5[1], backup_6[1]]
                df_7 = [backup_5[2], backup_6[2]]

                # Create the data dictionary to be saved as JSON
                data = {
                    "FADS Input": {
                        "Laser 488 Power": df_5,
                        "Laser 638 Power": df_6,
                        "Laser 405 Power": df_7,
                        "PMT1 Gain": df_3[0],
                        "PMT2 Gain": df_3[1],
                        "PMT1 Threshold": df_3[2],
                        "Scatter Plot Max Events": df_4
                    },
                    "PMT1 DataFrame": df_1.to_dict(orient="records"),
                    "PMT2 DataFrame": df_2.to_dict(orient="records"),
                    "Dot Plot DataFrame": df_0.to_dict(orient="records")
                }

                try:
                    # Save the data dictionary as JSON to the selected file
                    with open(file_path, "w") as f_output:
                        json.dump(data, f_output, indent=4)
                except Exception as e:
                    print(f"An error occurred while saving the file: {e}")
            else:
                print("No file selected.")

    def _toggle_changed(self, state):
        with self.dg_lock:
            if state:
                self.toggle.label = "Collecting"
                self.toggle.button_type = "success"
                self.dg.start_generating()
                self.no_update = 0 #LibreHub
            else:
                self.toggle.label = "Start"
                self.toggle.button_type = "primary"
                self.dg.stop_generating()
                self.no_update = 1 #LibreHub

    def _toggle_pmt_signal(self, attr, old, new):
        with self.dg_lock:
            if new == "PMT1":
                self.line_pmt1.visible = True
                self.line_pmt2.visible = False 
            
            if new == "PMT2":
                self.line_pmt1.visible = False
                self.line_pmt2.visible = True

            if new == "All":
                self.line_pmt1.visible = True
                self.line_pmt2.visible = True

    def _gain1_changed(self, attr, old, new):
        with self.dg_lock:
            self.dg.set_gain(new, 1)

    def _gain2_changed(self, attr, old, new):
        with self.dg_lock:
            self.dg.set_gain(new, 2)

    def _thresh_changed(self, attr, old, new):
        with self.dg_lock:
            self.dg.set_thresh(new)
            self.thresh_line.location = self.sliders[3].value

    def _spinner_changed(self, attr, old, new):
        with self.dg_lock:
            self.buffer_length = self.bufferspinner.value

    def _record_signal(self): #LibreHub
        with self.dg_lock:
            # Calculate the number of samples for 1 second
            sampling_interval_ms = 0.02  # Sampling interval in milliseconds
            samples_per_second = int(1000 / sampling_interval_ms)

            # Ensure data is being generated and capture 1 second of data
            recorded_1s_data = {
                "pmt1": {
                    "x": self.source_PMT1.data["x"][-samples_per_second:],  # Last 1 second of data
                    "y": self.source_PMT1.data["y"][-samples_per_second:],
                },
                "pmt2": {
                    "x": self.source_PMT2.data["x"][-samples_per_second:],  # Last 1 second of data
                    "y": self.source_PMT2.data["y"][-samples_per_second:],
                },
            }

            # Store this data in a file or a variable for further processing
            print(f"\n Data recorded for 1 second: \n{recorded_1s_data}")

    def _boxselect_changed(self):
        # Custom javascript callback for box select tool
        js_code ="""
            // Store selected geometry in variables
            var geometry = cb_obj.geometry;
            var x0 = geometry.x0;
            var y0 = geometry.y0;
            var x1 = geometry.x1;
            var y1 = geometry.y1;
                            
            // Log the values in the JS console:
            console.log('Sorting Gate xmin: ', x0);
            console.log('Sorting Gate ymin: ', y0);
            console.log('Sorting Gate xmax: ', x1);
            console.log('Sorting Gate ymax: ', y1);
            console.log('Geometry: ', geometry);

            // source_bx.data = geometry;
            source_bx.data = {
                'x0': [x0],
                'y0': [y0],
                'x1': [x1],
                'y1': [y1]
            };
            source_bx.change.emit();
        """
        callback = CustomJS(
            args=dict(source_bx=self.source_bx),
            code=js_code,
        )
        
        self.plot2d.js_on_event(SelectionGeometry, callback)
        self.source_bx.on_change("data", self._boxselect_pass)

    def _sub_boxselect_changed(self, plot_id): #LibreHub
        # Create a new ColumnDataSource for the selection geometry
        sub_source_bx_local = ColumnDataSource(data=dict(x0=[], y0=[], x1=[], y1=[]))
        self.sub_source_bx_dic[plot_id] = sub_source_bx_local
        # Custom javascript callback for box select tool
        js_code ="""
            // Store selected geometry in variables
            var geometry = cb_obj.geometry;
            var x0 = geometry.x0;
            var y0 = geometry.y0;
            var x1 = geometry.x1;
            var y1 = geometry.y1;
                            
            // Log the values in the JS console:
            console.log('Sorting Gate xmin: ', x0);
            console.log('Sorting Gate ymin: ', y0);
            console.log('Sorting Gate xmax: ', x1);
            console.log('Sorting Gate ymax: ', y1);
            console.log('Geometry: ', geometry);

            // source_bx.data = geometry;
            sub_source_bx.data = {
                'x0': [x0],
                'y0': [y0],
                'x1': [x1],
                'y1': [y1]
            };
            sub_source_bx.change.emit();
        """

        dynamic_callback = CustomJS(
            args=dict(sub_source_bx=sub_source_bx_local),
            code=js_code,
        )
        
        self.sub_plots_dic[plot_id].js_on_event(SelectionGeometry, dynamic_callback)
        sub_source_bx_local.on_change("data", lambda attr, old, new: self._sub_boxselect_pass(attr, old, new, plot_id))

    def _boxselect_pass(self, attr, old, new):
        with self.dg_lock:
            print("Box Select made on original plot")

            # Pass box values to the hardware class through the pipe to set gate values
            self.dg.set_gate_values(dict(new))

            # Store box values in ui box_select and update box select text
            self.boxselect = new
            self.custom_div.text = self._create_divhtml()
            plot_id = "plot_0" #LibreHub

            if plot_id in self.sub_plots_dic: #LibreHub
                plot0_fig = self.sub_plots_dic["plot_0"]
                plot0_data = self.sub_plots_source["plot_0"]
                # Retrieve box coordinates from the new selection, LibreHub
                x0, y0, x1, y1 = new["x0"][0], new["y0"][0], new["x1"][0], new["y1"][0]

                # Filter data points that are within the selected box, LibreHub
                main_data = self.source_2d.data
                selected_indices = [
                    i for i in range(len(main_data["x"]))
                    if x0 <= main_data["x"][i] <= x1 and y0 <= main_data["y"][i] <= y1
                ]

                # Update sub_data_source with selected data points, LibreHub
                plot0_data.data = {
                    "x": [main_data["x"][i] for i in selected_indices],
                    "y": [main_data["y"][i] for i in selected_indices],
                    "density": [main_data["density"][i] for i in selected_indices],
                }

                # Calculate new ranges with padding
                if selected_indices:
                    new_x_min = min(plot0_data.data['x'])
                    new_x_max = max(plot0_data.data['x'])
                    new_y_min = min(plot0_data.data['y'])
                    new_y_max = max(plot0_data.data['y'])

                    # Define padding factor (e.g., 10% of the range)
                    padding_factor = 0.15

                    # Calculate padding in logarithmic scale
                    x_padding_min = new_x_min / (1 + padding_factor)
                    x_padding_max = new_x_max * (1 + padding_factor)
                    y_padding_min = new_y_min / (1 + padding_factor)
                    y_padding_max = new_y_max * (1 + padding_factor)

                    # Apply padded ranges while maintaining logarithmic scale
                    plot0_fig.x_range.start = x_padding_min
                    plot0_fig.x_range.end = x_padding_max
                    plot0_fig.y_range.start = y_padding_min
                    plot0_fig.y_range.end = y_padding_max

                    # Ensure the tickers remain logarithmic
                    plot0_fig.xaxis.ticker = LogTicker(base=10, mantissas=[1], desired_num_ticks=4)
                    plot0_fig.yaxis.ticker = LogTicker(base=10, mantissas=[1], desired_num_ticks=4)

    def _sub_boxselect_pass(self, attr, old, new, plot_id): #LibreHub
        with self.dg_lock:
            # Your implementation for handling the box select pass
            print(f"Box Select made on plot with ID: {plot_id}")
            plot_unit = int(plot_id.split("_")[1])
            next_plot_id = f"plot_{plot_unit + 1}"
            # Pass box values to the hardware class through the pipe to set gate values
            self.dg.set_gate_values(dict(new))

            # Store box values in ui box_select and update box select text
            self.sub_boxselect = new
            self.dynamic_widgets_container.children[plot_unit].children[0].text = self._create_sub_divhtml()
            
            if next_plot_id in self.sub_plots_dic:
                # Retrieve box coordinates from the new selection, LibreHub
                x0, y0, x1, y1 = new["x0"][0], new["y0"][0], new["x1"][0], new["y1"][0]

                # Filter data points that are within the selected box, LibreHub
                main_data = self.sub_plots_source[plot_id].data
                selected_indices = [
                    i for i in range(len(main_data["x"]))
                    if x0 <= main_data["x"][i] <= x1 and y0 <= main_data["y"][i] <= y1
                ]

                # Update sub_data_source with selected data points, LibreHub
                self.sub_plots_source[next_plot_id].data = {
                    "x": [main_data["x"][i] for i in selected_indices],
                    "y": [main_data["y"][i] for i in selected_indices],
                    "density": [main_data["density"][i] for i in selected_indices],
                }

                # Calculate new ranges with padding
                if selected_indices:
                    new_x_min = min(self.sub_plots_source[next_plot_id].data['x'])
                    new_x_max = max(self.sub_plots_source[next_plot_id].data['x'])
                    new_y_min = min(self.sub_plots_source[next_plot_id].data['y'])
                    new_y_max = max(self.sub_plots_source[next_plot_id].data['y'])

                    # Define padding factor (e.g., 10% of the range)
                    padding_factor = 0.15

                    # Calculate padding in logarithmic scale
                    x_padding_min = new_x_min / (1 + padding_factor)
                    x_padding_max = new_x_max * (1 + padding_factor)
                    y_padding_min = new_y_min / (1 + padding_factor)
                    y_padding_max = new_y_max * (1 + padding_factor)

                    # Apply padded ranges while maintaining logarithmic scale
                    self.sub_plots_dic[next_plot_id].x_range.start = x_padding_min
                    self.sub_plots_dic[next_plot_id].x_range.end = x_padding_max
                    self.sub_plots_dic[next_plot_id].y_range.start = y_padding_min
                    self.sub_plots_dic[next_plot_id].y_range.end = y_padding_max

                    # Ensure the tickers remain logarithmic
                    self.sub_plots_dic[next_plot_id].xaxis.ticker = LogTicker(base=10, mantissas=[1], desired_num_ticks=4)
                    self.sub_plots_dic[next_plot_id].yaxis.ticker = LogTicker(base=10, mantissas=[1], desired_num_ticks=4)

    def manage_laser_live_status(self):           
        # Laser Parameters called, LibreHub
        if self.init_COM_toggle.button_type == 'success':
            #Channel status
            ch1_status = self.serial_manager.get_ch1_status()
            ch2_status = self.serial_manager.get_ch2_status()
            ch3_status = self.serial_manager.get_ch3_status()

            #Power info
            ch1_power = self.serial_manager.get_ch1_pw()
            ch2_power = self.serial_manager.get_ch2_pw()
            ch3_power = self.serial_manager.get_ch3_pw()

            #Channel failure
            ch1_failure = self.serial_manager.get_ch1_failure()
            ch2_failure = self.serial_manager.get_ch2_failure()
            ch3_failure = self.serial_manager.get_ch3_failure()

        # Laser Layout in Bokeh, LibreHub
            #Channel power
            self.LASER_live[0].value = str(ch1_power)
            self.LASER_live[1].value = str(ch2_power)
            self.LASER_live[2].value = str(ch3_power)
            #Channel status
            self.LASER_status_code[0].value = f"LASER 1: {str(ch1_status)}"
            self.LASER_status_code[1].value = f"LASER 2: {str(ch2_status)}"
            self.LASER_status_code[2].value = f"LASER 3: {str(ch3_status)}"

            #Channel failure
            if ch1_failure != "[]" or ch2_failure != "[]" or ch3_failure != "[]":
                self.custom_COM_3.button_type = "danger"
                self.custom_COM_2.value = f"LASER 1: {ch1_failure}, LASER 2: {ch2_failure}, LASER 3: {ch3_failure}"
            else:
                self.custom_COM_2.value = "No Error Detected"
                if self.custom_COM_3.button_type == "danger":
                    self.custom_COM_3.button_type = "success"

    def manage_timers(self):
        """This is just a simple way to keep track of how long the update_ui function takes to run."""
        self.timers = np.roll(self.timers, 1)
        self.timers[0] = time.perf_counter()
        rate_seconds_per_update = np.mean(np.diff(self.timers)) * -1
        self.plot.title.text = f"Update Rate: {1/rate_seconds_per_update:.01f} Hz ({rate_seconds_per_update*1000:.00f} ms)"

    def update_ui(self):
        """Pull data from the hardware (in another process) and update the data source and plot"""
        with self.dg_lock:
            #Live Data Points
            if self.toggle.label == "Collecting":
                self.GATE_data_points.value = str(len(self.source_2d.data["x"]))

            # Update pmt data
            self.source_PMT1.data = self.dg.data["pmt1"]
            self.source_PMT2.data = self.dg.data["pmt2"]

            if self.no_update == 0 or self.toggle.label == "Collecting":
                for key in self.rolling_source_2d:
                    self.rolling_source_2d[key].extend(self.dg.data2d[key])
                    if self.buffer_length == 0:
                        self.rolling_source_2d[key] = [np.nan]
                    elif len(self.rolling_source_2d[key]) > self.buffer_length:
                        self.rolling_source_2d[key] = self.rolling_source_2d[key][
                            -self.buffer_length :
                        ]

                self.source_2d.data = self.rolling_source_2d

            self.manage_timers()
            self.manage_laser_live_status()

ui = UI()