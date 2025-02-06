# Piccolo - the GUI of [RITMOS](https://github.com/wenzel-lab/droplet-sorter-master) [![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)

See the [droplet sorter master repository](https://github.com/wenzel-lab/droplet-sorter-master) for more detail.
The Python + Bokeh based graphical user interfac (GUI), run on a desktop computer, communicates closely with the [RedPitaya computer brain of the droplet sorter, documented here](https://github.com/wenzel-lab/droplet-sorting-FPGA-controller), which contains the [communication architecture design for the GUI](https://github.com/wenzel-lab/droplet-sorting-FPGA-controller/wiki/GUI-Architecture). 
This repository holds the GUI code, the interaface mockups, and the development wishlist.

Follow us! [#twitter](https://twitter.com/WenzelLab), [#YouTube](https://www.youtube.com/@librehub), [#LinkedIn](https://www.linkedin.com/company/92802424), [#instagram](https://www.instagram.com/wenzellab/), [#Printables](https://www.printables.com/@WenzelLab), [#LIBREhub website](https://librehub.github.io), [#IIBM website](https://ingenieriabiologicaymedica.uc.cl/en/people/faculty/821-tobias-wenzel)

---

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [Contribute](#contribute)
- [License](#license)
- [Contacts](#contacts)

---

## Introduction
Piccolo provides tools for droplet processing instruments. This project provides a user-friendly interface for sorting droplets and visualizing data from multiple detectors. It is built using Bokeh for interactive visualizations.

---

## Features
- Interactive data visualization of droplets in microfluidic fluorescence-activated droplet sorter
- Display and interact with data across different channels and set sorting gates in a UI
- Customizable settings for sorting and laser modules
- Support for multiple detectors and RS232 lasers

---

## Installation

> [!WARNING]
> Firstly, make sure you have conda installation and environment in your device:
```
conda info
conda create --name <your environment>
conda activate <your environment>
```

To install the necessary dependencies, make use of our .yml file and run:

` conda env update -n <your environment> --file bokeh_2.yml`

---

## Usage
> [!IMPORTANT] 
> Make sure all dependencies are installed, active and properly located.

Run: 

` bokeh serve --show ui_layout.py`

---

## Organization

1. #### LASER CONTROLS:
    ![ScreenShot](/images/laser_controls.png?raw=true)

2. #### DROPLET VISUALIZATION:
    ![ScreenShot](/images/droplet_visualization.png?raw=true)

3. #### SIGNAL VISUALIZATION:
    ![ScreenShot](/images/signal_visualization.png?raw=true)

4. #### SORTING CONTROLS:
    ![ScreenShot](/images/sorting_controls.png?raw=true)

---

## Dependencies

The main dependencies for this project are:

- `bokeh`
- `numpy`
- `pandas`
- `pyserial`
- `requests`
- `scipy`
- `tornado`
- `websockets`

These and additional dependencies can be found in `bokeh_2.yml`.

---

## Contribute

This is an open project in the Wenzel Lab in Santiago, Chile. If you have any suggestions to improve it or add any additional functions make a pull-request or [open an issue](https://github.com/wenzel-lab/droplet-sorter-master/issues/new).
For interactions in our team and with the community applies the [GOSH Code of Conduct](https://openhardware.science/gosh-2017/gosh-code-of-conduct/).


---

## License

Apache 2.0


---

#### Contacts

Joaquín Acosta - Pontificia Universidad Católica de Chile
Tobias Wenzel - Pontificia Universidad Católica de Chile
Kendra Nyberg - Calico Life Sciences LLC
