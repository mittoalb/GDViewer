# GDViewer

A Globus ZARR viewer using ImageJ. Works with linux only (for now). It requires FIJI installed on your system.
FIJI can be found: https://imagej.net/software/fiji/downloads


## Installation


Create a conda environment and activate it:
```bash
conda create -n GDViewer
conda activate GDViewer
```
Download and install the package:

```bash
git clone https://github.com/mittoalb/GDViewer.git
cd GDViewer
pip install .
```
Use:
```bash
python -m GDViewer.main
```

