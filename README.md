# Piccolo - the GUI of Ritmos [![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)

See the [droplet sorter master repository](https://github.com/wenzel-lab/droplet-sorter-master) for more detail.
The Python + Bokeh based graphical user interfac (GUI), run on a desktop computer, communicates closely with the [RedPitaya computer brain of the droplet sorter, documented here](https://github.com/wenzel-lab/droplet-sorting-FPGA-controller), which contains the [communication architecture design for the GUI](https://github.com/wenzel-lab/droplet-sorting-FPGA-controller/wiki/GUI-Architecture). 
This repository holds the GUI code, the interaface mockups, and the development wishlist.

Follow us! [#twitter](https://twitter.com/WenzelLab), [#YouTube](https://www.youtube.com/@librehub), [#LinkedIn](https://www.linkedin.com/company/92802424), [#instagram](https://www.instagram.com/wenzellab/), [#Printables](https://www.printables.com/@WenzelLab), [#LIBREhub website](https://librehub.github.io), [#IIBM website](https://ingenieriabiologicaymedica.uc.cl/en/people/faculty/821-tobias-wenzel)

#### 

Piccolo provides tools for droplet processing instruments:

1. Generate test data of droplets in microfluidic fluorescence-activated droplet sorter 
2. Display and interact with test data across different channels and set sorting gates in a UI


![ScreenShot](/preview_bokeh_screenshot.png?raw=true)

---

#### Quickstart

Run with `bokeh serve --show ui_layout.py`


---

#### Dependencies

| Dependency | Version |
|------------|---------|
| _libgcc_mutex | 0.1 |
| _openmp_mutex | 4.5 |
| bokeh | 3.4.1 |
| bzip2 | 1.0.8 |
| ca-certificates | 2024.2.2 |
| colorama | 0.4.6 |
| contourpy | 1.2.1 |
| freetype | 2.12.1 |
| jinja2 | 3.1.3 |
| lcms2 | 2.16 |
| ld_impl_linux-64 | 2.40 |
| lerc | 4.0.0 |
| libblas | 3.9.0 |
| libcblas | 3.9.0 |
| libdeflate | 1.20 |
| libexpat | 2.6.2 |
| libffi | 3.4.2 |
| libgcc-ng | 13.2.0 |
| libgfortran-ng | 13.2.0 |
| libgfortran5 | 13.2.0 |
| libgomp | 13.2.0 |
| libjpeg-turbo | 3.0.0 |
| liblapack | 3.9.0 |
| libnsl | 2.0.1 |
| libopenblas | 0.3.27 |
| libpng | 1.6.43 |
| libsqlite | 3.45.2 |
| libstdcxx-ng | 13.2.0 |
| libtiff | 4.6.0 |
| libuuid | 2.38.1 |
| libwebp-base | 1.4.0 |
| libxcb | 1.15 |
| libxcrypt | 4.4.36 |
| libzlib | 1.2.13 |
| markupsafe | 2.1.5 |
| ncurses | 6.4.20240210 |
| numpy | 1.26.4 |
| openjpeg | 2.5.2 |
| openssl | 3.2.1 |
| packaging | 24.0 |
| pandas | 2.2.2 |
| pillow | 10.3.0 |
| pip | 24.0 |
| pthread-stubs | 0.4 |
| pyserial | 3.5 |
| python-dateutil | 2.9.0 |
| python-tzdata | 2024.1 |
| python | 3.12.3 |
| python_abi | 3.12 |
| pytz | 2024.1 |
| pyyaml | 6.0.1 |
| readline | 8.2 |
| scipy | 1.13.0 |
| setuptools | 69.5.1 |
| six | 1.16.0 |
| tk | 8.6.13 |
| tornado | 6.4 |
| tqdm | 4.66.2 |
| tzdata | 2024a |
| wheel | 0.43.0 |
| xorg-libxau | 1.0.11 |
| xorg-libxdmcp | 1.1.3 |
| xyzservices | 2024.4.0 |
| xz | 5.2.6 |
| yaml | 0.2.5 |
| zstd | 1.5.5 |

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
