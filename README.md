# Programing for Data Science

This is a Project for PHBO AI at HU module Programming for Datascience in Python

There is a environment.yml created of the Anaconda Python environment. This can be used for creating the environment.
```bash
conda env export > environment.yml
```

Cloning github repository.
```bash
git clone https://github.com/jletteboer/P4DS.git
```

Go to directory.
```bash
cd PD4S
```

Create an environment using the environment.yml file.
```bash
conda env create --name p4ds-student --file environment.yml
```

Activate new environment fore using it.

**Windows:**
```bash
activate p4ds-student
```

**MacOS:**
```bash
source activate p4ds-student
```

```bash
jupyter notebook
```

The directory tree of the project looks:
```bash
P4DS/
├── Project
│   ├── data
│   │   ├── IP2LOCATION-LITE-DB5
│   │   │   ├── IP2LOCATION-LITE-DB5.BIN
│   │   │   ├── LICENSE_LITE.TXT
│   │   │   └── README_LITE.TXT
│   │   ├── p4ds_weblog_alm.csv.zip
│   │   └── p4ds_weblog_small.csv.zip
│   └── notebooks
│       ├── Project P4DS.ipynb
│       ├── functions.py
│       └── media
│           ├── CRISP-DM_Process_Diagram.png
│           ├── downloadData.mp4
│           └── iqr.png
├── README.md
└── environment.yml

5 directories, 12 files
```