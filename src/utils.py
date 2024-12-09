import pandas as pd
import yaml
from pathlib import Path
import requests

########## Load config.yaml ##########
def load_config(path: str, filepaths: bool=True, **kwargs):

    #load config.yaml as dict
    with open(path, "r") as handle:
        config = yaml.safe_load(handle)

    # Navigate through the config dictionary if kwargs are provided
    for key in kwargs.values():
        if key not in config:
            raise KeyError(f"Key '{key}' not found in the config.yaml")
        config = config[key]

    # Convert string paths to Path objects if filepaths is True
    if filepaths:
        config = {k: Path(v) if isinstance(v, str) else v for k, v in config.items()}

    return config


########## Run SPARQL query via requests ##########
def run_sparql_query(query):
    url = "https://query.wikidata.org/sparql"
    headers = {'Accept': 'application/sparql-results+json',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    params = {'query': query}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  #raise error for bad responses
    return response.json()


########## Check for substructure presence ##########
def check_substructure(mol, substruct_list):  # function to filter substructures
    return mol is not None and any(mol.HasSubstructMatch(sub) for sub in substruct_list)