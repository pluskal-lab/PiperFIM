#individually run SPARQL queries (stored in scripts/sparql_queries), clean results (e.g., remove duplicates) and saves ouptut in data/wikidata

import pandas as pd
import requests
from pathlib import Path
from src.utils import load_config, run_sparql_query
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


#config.yaml
config = load_config(path='config/config.yaml', section='wikidata')

#run SPARQL queries for each scaffold
queries_dict = config['sparql_queries']

for scaffold in queries_dict.keys():
    logging.info(f'Running SPARQL query for the {scaffold} scaffold.')
    query_path = Path(queries_dict.get(scaffold)) #get query path for the scaffold
    if query_path.exists():
        logging.info(f'Query successfully imported...')
        query = query_path.read_text()
    else:
        logging.error(f'No query found at {query_path}.')
        continue

    try:
        query_out = run_sparql_query(query) #run query
        logging.info(f'Query successfully run! Cleaning results...')
        
        #convert query output (json) to pandas df
        output_df = pd.json_normalize(query_out['results']['bindings']) #flatten json to df
        output_df = output_df[[col for col in output_df.columns if col.endswith('.value')]] #keep '.value' columns
        output_df.columns = [col.replace('.value', '') for col in output_df.columns] #remove '.value' from column names

        #if genus_name made of multiple words (e.g., full species name), keep first word
        output_df['genus_name'] = output_df['genus_name'].apply(lambda x: x.split()[0])
        output_df = output_df.drop_duplicates(subset=['genus_name', 'smiles', 'reference']) #drop potentially-generated duplicates
        logging.info(f"""The {scaffold} query returned {len(output_df['smiles'].drop_duplicates())} unique structures in {len(output_df['genus_name'].drop_duplicates())} genera, based on {len(output_df['reference'].drop_duplicates())} literature references.""")
        
        #save query output as csv
        output_path = Path(f'data/wikidata/{scaffold}_in_genera.csv')
        output_df.to_csv(output_path, index=False)
        logging.info(f'Query results saved in {output_path}')

    except requests.exceptions.HTTPError as http_err:
        logging.error((f"HTTP error occurred: {http_err}"))
    except Exception as err:
        logging.error((f"An error occurred: {err}"))