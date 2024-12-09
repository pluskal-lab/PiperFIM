import os
import pandas as pd
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import Draw
from IPython.display import display
from src.utils import load_config, check_substructure
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


#import config.yaml and scaffolds list
config = load_config(path='config/config.yaml', section='wikidata')
scaffold_list = config['scaffolds']

for scaffold in scaffold_list:
    logging.info(f'Cleaning raw SPARQL query output for the following scaffold: {scaffold}')
    
    #import raw SPARQL output
    data_path = Path(config['sparql_results'].get(scaffold))
    data = pd.read_csv(data_path)
    logging.info(f'Importing raw SPARQL output from {data_path}....')

    ###Filter substructures
    struct_to_remove = config['unwanted_structures'].get(scaffold) #get substructures 

    if struct_to_remove:
        struct_to_remove = [Chem.MolFromSmiles(s) for s in struct_to_remove]  # Convert SMILES to RDKit molecule objects
        logging.info(f"{len(struct_to_remove)} substructures being filtered from the raw SPARQL output of the '{scaffold}' scaffold...")

        #apply filter
        data.loc[:, 'structure'] = data['smiles'].map(Chem.MolFromSmiles)  # create 'structure' column
        ids_to_remove = data['structure'].apply(lambda mol: check_substructure(mol, struct_to_remove))
        data_clean = data[~ids_to_remove]  #remove matched substructures
        logging.info(f"{ids_to_remove.sum()} structures filtered from the raw SPARQL output for the '{scaffold}' scaffold!")

    else:
        logging.info(f"No substructures to filter for the '{scaffold}' scaffold!")
        data_clean = data


    ###Filter wrong Wikidata report (manual inspection)
    genera_to_remove = config['errors'].get(scaffold) #get manual fixes
    if genera_to_remove:
        logging.info(f"Removing the following genera from the raw SPARQL output for the '{scaffold}' scaffold: {', '.join(genera_to_remove)}")
        n_removed_entries = data_clean['genus_name'].isin(genera_to_remove).sum()
        logging.info(f"{n_removed_entries} entries removed...")
        data_clean_man = data_clean[~data_clean['genus_name'].isin(genera_to_remove)]
    else:
        logging.info(f"No genera to remove for the '{scaffold}' scaffold!")
        data_clean_man = data_clean

    #save clean data
    output_path = Path('results/phylo_tree/wikidata_clean') / (data_path.stem + '_clean' + data_path.suffix)
    data_clean_man.to_csv(output_path, index=False)
    logging.info(f'Cleaned data saved in {output_path}')