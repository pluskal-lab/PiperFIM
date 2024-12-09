import yaml
from pathlib import Path
import pandas as pd
import numpy as np
import networkx as nx
import requests
from rdkit import Chem
from rdkit.Chem import Draw


# ########## Load config.yaml file ##########

# def load_config(config_path='./config.yaml', section=None, subsection=None):

#     with open(config_path, "r") as handle:
#         config = yaml.safe_load(handle)
#         print(f"Full config: {config}")
#     if subsection:
#         return config.get(subsection, {})
#     else:
#         return config.get(section, {}) 
    

########## Load config.yaml files ########## TODELETE
# def get_config(config_path, **kwargs):
    
#     #load config.yaml as dict
#     with open(config_path, "r") as handle:
#         config = yaml.safe_load(handle)
    
#     #keep portion of config.yaml based on provided keys 
#     try:
#         for level in kwargs.values():
#             config = config[level]
        
#         #convert str paths to Path objects
#         config = {k: Path(v) if isinstance(v, str) else v for k, v in config.items()}

#         return config
#     except KeyError:
#         raise KeyError("Key(s) not found in config.yaml")



########## Apply signal intensity threshold ##########

def apply_threshold(feature_table, sample_columns, intensity_threshold = 0):

    """
    Entries < `intensity_threshold` are set to 0. Set `intensity_threshold = 0` to disable.
    """
    
    nonzero_before = np.count_nonzero(feature_table[sample_columns].values)
    
    for column in sample_columns:
        feature_table.loc[feature_table[column] < intensity_threshold, column] = 0

    nonzero_after = np.count_nonzero(feature_table[sample_columns].values)
    thresholded_entries = nonzero_before - nonzero_after

    print('A total of', thresholded_entries, 'entries were thresholded')
    
    return feature_table


########## Display features annotated by SIRIUS ##########

def display_annotated_features(feature_table, sample_name, min_ConfidenceScore = 0.5, sort_by = 'ConfidenceScore', maxmols = 50):
    """
    Displays features annotated by SIRIUS in a specific sample.

    Parameters:
    - feature_table (pandas DataFrame): MZmine feature table.
    - sample_name (str): Samples' name (column name) in the feature table.
    - min_ConfidenceScore (float, optional): Minimum ConfidenceScore threshold. Defaults to 0.5.
    - sort_by (str, optional): column name to sort the feature table by. Defaults to 'ConfidenceScore'.
    - maxmols (int, optional): Maximum number of molecules to display. Defaults to 100.

    Returns:
    - PIL.Image.Image or SVG: RDKit image object.

    """

    df = feature_table.loc[(feature_table[sample_name] > 0) & (feature_table['ConfidenceScore'] > min_ConfidenceScore)].sort_values(by=sort_by, ascending=False)

    #convert smiles to RDKit molecules
    mols = [Chem.MolFromSmiles(smile) for smile in df['smiles']]

    feat_ID = df['feat_ID'].astype(str).tolist()
    scores = round(df['ConfidenceScore'], 2).astype(str).tolist()
    labels = []

    for feat_ID, score in zip(feat_ID, scores):
        labels.append(f"{feat_ID} (COSMSIC = {score})")
    
    #display RDKit molecules
    return Draw.MolsToGridImage(mols, molsPerRow=5, legends=labels, maxMols=maxmols, subImgSize=(450,300), useSVG=True)

##############################


"""
Sort CANOPUS chemical classes (Pathway)
"""

def pathway_order(p):
    """
    Add docstring
    """

    if p == 'Alkaloids': return 1
    elif p == 'Shikimates and Phenylpropanoids': return 2
    elif p == 'Terpenoids': return 3
    elif p == 'Polyketides': return 4
    elif p == 'Amino acids and Peptides': return 5
    elif p == 'Fatty acids': return 6
    return 7

##############################


"""
Sort CANOPUS chemical classes (alkaloid classes)
"""

def alkclass_order(p):
    """
    Add docstring
    """

    if p == 'Piperidine alkaloids': return 1
    elif p == 'Isoquinoline alkaloids': return 2
    elif p == 'Pyridine alkaloids': return 3
    elif p == 'Simple amide alkaloids': return 4
    elif p == 'Quinoline alkaloids': return 5
    elif p == 'Simple indole alkaloids': return 6
    elif p == 'Purine alkaloids': return 7
    return 8

##############################


"""
Import and clean GNPS node table
"""

def import_gnps(file_path):
    """
    Add docstring
    """
    
    #import node table
    graph = nx.read_graphml(file_path)
    
    #create node table
    node_table = pd.DataFrame([dict(attributes, feat_ID=int(node_id)) for node_id, attributes in graph.nodes(data=True)])
    
    #create log-transformed intensity columns
    node_table['Log2_intensity'] = np.log2(node_table['sum(precursor intensity)'])
    node_table['Log10_intensity'] = np.log10(node_table['sum(precursor intensity)'])
    
    #create network_zie column
    network_size = node_table.groupby('componentindex')['componentindex'].count()
    node_table = node_table.merge(network_size, how='left', left_on ='componentindex', right_index=True, suffixes = (None, '_count'))
    node_table.rename(columns={'componentindex_count': 'network_size'}, inplace=True)

    return node_table

##############################


"""
Send SPARQL query via requests
"""
def run_sparql_query(query):
    url = "https://query.wikidata.org/sparql"
    headers = {'Accept': 'application/sparql-results+json',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    params = {'query': query}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  #raise error for bad responses
    return response.json()