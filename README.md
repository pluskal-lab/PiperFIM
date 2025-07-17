# Computational metabolomics reveals overlooked chemodiversity of alkaloid scaffolds in *Piper fimbriulatum*
This repository contains all the scripts needed to reproduce the data analysis and results of the manuscript "Computational metabolomics reveals overlooked chemodiversity of alkaloid scaffolds in *Piper fimbriulatum*" (https://doi.org/10.1111/tpj.70086).

## Requirements
- [mzmine](https://mzio.io/mzmine-news/) software (v4.2.0)
- [SIRIUS](https://bio.informatik.uni-jena.de/software/sirius/) software (v5.8.5)
- [GNPS2](https://gnps2.org/homepage) online platform
- [Miniconda/Anaconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)
- Python 3.11.0 or higher


## Installation and setup
1. To install mzmine and SIRIUS, follow the instructions provided in the corresponding online documentation (see [mzmine](https://mzmine.github.io/mzmine_documentation/index.html) and [SIRIUS](https://boecker-lab.github.io/docs.sirius.github.io/) docs).

2. Concerning this GitHub repository, clone it by running the following command in your terminal:
~~~
git clone https://github.com/pluskal-lab/PiperFIM.git
~~~

3. If you are a **Windows** user, create a new conda environment and install the required packages and dependencies from `requirements.yaml`:
~~~
conda env create -f requirements.yaml
conda activate piperfim
~~~

Before, running any scripts, set the `PYTHONPATH` to the project root so that internal imports work correctly:
~~~
$env:PYTHONPATH = "$(Get-Location)"
~~~

Alternatively, if you are using **macOS or Linux**, you can run the `activate.sh` script:
~~~
source activate.sh
~~~

4. Download the `data` and `results` folder from [Zenodo](https://zenodo.org/records/14337379) inside the main repository directory.

> [!NOTE]
> Paths and names of all input and output files are listed in the `config/config.yaml` file and can be changed directly from there.

## Usage
### LC-MS data analysis
Feature detection with mzmine can be reproduced using the provided batch file (`mzmine_featdetect.mzbatch` in the `scripts` folder) as described in [Heuckeroth et al. 2024](https://www.nature.com/articles/s41596-024-00996-y). Feature-based molecular networking (FBMN) on the GNPS2 platform and _in silico_ chemical structure and compound class predictions with the SIRIUS software can be reproduced as described in the [original publication]([bioRchive_DOI](https://doi.org/10.1101/2024.12.10.627739)). 


The `01_lcms_dataprep.py` integrates output files from these software tools to facilitate downstream data analysis:
~~~
python scripts/01_lcms_dataprep.py
~~~
This will produce two output files: `ftable_clean.csv` (mzmine-like feature table) and `ntable_clean.csv` (GNPS2-like node table). The first can be used to perform statistical analysis, while the second can be imported in Cytoscape for enhanced exploration of FBMN results.


### SPARQL query
The `02_run_sparql_queries.py` script runs the SPARQL queries stored in the `scripts/sparql_queries` folder, clean the results (e.g., remove duplicates) and saves the output in the `data/wikidata` folder. Queries are designed to retrieve all natural products that contain a specific substructure (defined by a SMILES) together with the plant genera each compound was isolated from, based on Wikidata. Literature references are also retrieved.
~~~
python scripts/02_run_sparql_queries.py
~~~

The `03_clean_wikidata.py` script cleans raw SPARQL query outputs by filtering out "unwanted substructures" erroneous reports in Wikidata as defined in the `config.yaml` file. Cleaned results are saved in the `results/phylo_tree/wikidata_clean` folder.

~~~
python scripts/03_run_sparql_queries.py
~~~

### Map SPARQL results onto the Angiosperm tree of life
The `04_create_itol_annotation.py` script creates an annotation file (`iTOL_scaffolds.txt`) to use in [iTOL](https://itol.embl.de/) to map literature reports for each alkaloid scaffold (i.e., benzylisoquinoline, aporphine, piperolactam, piperidine, _seco_-benzylisoquinoline) in each genus covered in the angiosperm tree of life published by [Zuntini et al. 2024](https://www.nature.com/articles/s41586-024-07324-0) (`global_tree_brlen_pruned_renamed.tre` file). The resulting tree can be accessed at the following [link](https://itol.embl.de/tree/14723112167277531728383616).

The `05_create_small_tree.py` script creates a smaller version of the `global_tree_brlen_pruned_renamed.tre` file by keeping only the orders where at least one alkaloid scaffold was reported. The resulting tree can be accessed at the following [link](https://itol.embl.de/tree/14723112167224931731658296).
