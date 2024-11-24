# PiperFim Project
This repository contains all the scripts needed to reproduce the data analysis and results of the manuscript "Remarkable diversity of alkaloid scaffolds in *Piper fimbriulatum*". <!-- Add DOI when available -->

## Requirements
- [mzmine software](https://mzio.io/mzmine-news/) (v4.2.0)
- [SIRIUS software](https://bio.informatik.uni-jena.de/software/sirius/) (v5.8.5)
- [GNPS2](https://gnps2.org/homepage) online platform
- [Miniconda/Anaconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)
- Python 3.11.0 or higher


## Installation and steup
1. Clone the PiperFIM repository:
~~~
git clone https://github.com/titodamiani/PiperNET.git
~~~
<!-- Update link -->

2. Create a conda environment and install all  packages and dependencies listed in the `requirements.txt` file:

~~~
conda create -y --name piperfim
conda install --file requirements.txt -y
conda activate piperfim
~~~

3. Since data files are too big for GitHub, they are stored in [this](https://drive.google.com/drive/folders/15UYWvmtI2sL41GpBTNRzfWILiIslAqTf?usp=drive_link) Google Drive folder. Download the `data` folder inside the main PiperFim repository.

## Run scripts
### LC-MS data preparation
The `01_lcms_dataprep.py` script integrates various output files from the mzmine, SIRIUS and GNPS2 software tools into two data tables (i.e., `ftable_clean.csv` and `ntable_clean.csv`) to facilitate downstream data analysis. The `ftable_clean.csv` is an mzmine-like feature table and can be used to perform statistical analysis. The `ntable_clean.csv` is a GNPS2-like node table and can be used in Cytoscape for enhanced exploration of the  feature-based molecular networking results.

To run the script, move to the main repository and run:
~~~
python scripts/01_lcms_dataprep.py
~~~

Paths to all input and output files are listed in the `config.yaml`. Therefore, name or path to an input/ouput file can be changed directly from there.

### SPARQL query
The `02_run_sparql_queries.py` script runs the SPARQL queries stored in the `scripts/sparql_queries` folder, clean the results (e.g., remove duplicates) and saves the ouptut in the `data/wikidata` folder.

The SPARQL queries are designed to retrieve from Wikidata all natural products that contain a specific substructure (defined by a SMILES in the query), together with the name(s) of the plant genus each compound was isolated from. Literature references are also retrieved.