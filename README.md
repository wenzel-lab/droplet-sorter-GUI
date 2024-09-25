# Piccolo - the GUI of Ritmos [![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)

See the [droplet sorter master repository](https://github.com/wenzel-lab/droplet-sorter-master) for more detail.
The Python + Bokeh based graphical user interfac (GUI), run on a desktop computer, communicates closely with the [RedPitaya computer brain of the droplet sorter, documented here](https://github.com/wenzel-lab/droplet-sorting-FPGA-controller), which contains the [communication architecture design for the GUI](https://github.com/wenzel-lab/droplet-sorting-FPGA-controller/wiki/GUI-Architecture). 
This repository holds the GUI code, the interaface mockups, and the development wishlist.

Follow us! [#twitter](https://twitter.com/WenzelLab), [#YouTube](https://www.youtube.com/@librehub), [#LinkedIn](https://www.linkedin.com/company/92802424), [#instagram](https://www.instagram.com/wenzellab/), [#Printables](https://www.printables.com/@WenzelLab), [#LIBREhub website](https://librehub.github.io), [#IIBM website](https://ingenieriabiologicaymedica.uc.cl/en/people/faculty/821-tobias-wenzel)

#### 

Piccolo provides tools for droplet processing instruments:

1. Generate test data of droplets in microfluidic fluorescence-activated droplet sorter 
2. Display and interact with test data across different channels and set sorting gates in a UI


![ScreenShot](/screenshot.png?raw=true)

---

#### Quickstart

Run with `bokeh serve --show ui_layout.py`


---

#### Dependencies

python >= 3.8.5\
bokeh = 3.4.1

---

#### Contacts

Joaquín Acosta - Pontificia Universidad Católica de Chile
Tobias Wenzel - Pontificia Universidad Católica de Chile
Kendra Nyberg - Calico Life Sciences LLC

---

## Contribute

This is an open project in the Wenzel Lab in Santiago, Chile. If you have any suggestions to improve it or add any additional functions make a pull-request or [open an issue](https://github.com/wenzel-lab/droplet-sorter-master/issues/new).
For interactions in our team and with the community applies the [GOSH Code of Conduct](https://openhardware.science/gosh-2017/gosh-code-of-conduct/).


---

## License

Apache 2.0
