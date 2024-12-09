import pandas as pd
from Bio import Phylo
import yaml
import numpy as np
from pathlib import Path
import logging
from src.utils import load_config
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')



#load config
config = load_config(path='config/config.yaml', section='wikidata')

#import scaffold list
scaffold_list = config['scaffolds']

#import cleaned sparql results, concatenate into single df
scaffold_df = []
for scaffold, path in config['sparql_results_clean'].items():
    df = pd.read_csv(path)
    df['Scaffold'] = scaffold
    scaffold_df.append(df)
scaffold_df = pd.concat(scaffold_df, ignore_index=True)

#import Angiosperms tree
tree_file_path = Path(config['tree_file'])
tree = Phylo.read(tree_file_path, 'newick')
logging.info(f'Angiosperms phylogenetic tree successfully imported!')

#convert tree into df with order, family, genus, species
tree_leaves = [leaf.name for leaf in tree.get_terminals()] #extract leaf names
tree_leaves = pd.Series(tree_leaves, name='leaf_name')
tree_df = tree_leaves.str.split('_', expand=True)
tree_df = tree_df.iloc[:, :4] #keep first 4 columns
tree_df.columns = ['Order', 'Family', 'Genus', 'Species']
tree_df = pd.concat([tree_leaves, tree_df], axis=1).rename(columns={0: 'leaf_name'}).set_index('leaf_name')

#add binary column for each scaffold
for s in scaffold_list:
    tree_df[s] = 0  #create zero column
    genera_list = scaffold_df[scaffold_df['Scaffold'] == s]['genus_name'].unique() #list of genera with report (for each scaffold)

    #if genus with report present in the tree, set to 1
    for g in genera_list:
        tree_df.loc[tree_df['Genus'] == g, s] = 1  

#keep only orders with reported scaffolds
scaff_in_orders = tree_df.groupby('Order')[scaffold_list].sum()
scaff_in_orders = scaff_in_orders[scaff_in_orders.sum(axis=1) != 0] #drop rows with no scaffold

#remove nodes from orders with no scaffold
nodes_to_remove = tree_df[~tree_df['Order'].isin(scaff_in_orders.index)].index.to_list()
for n in nodes_to_remove:
    clade = tree.find_any(name=n)
    if clade:
        tree.prune(clade)
        logging.info(f"{n} leaf removed from tree...")
    else:
        logging.warning(f"{n} leaf not found in the tree.")

# Save the modified tree to a new file
output_path = tree_file_path.with_name(tree_file_path.stem + '_small' + tree_file_path.suffix)
Phylo.write(tree, output_path, "newick")
logging.info(f'Small tree saved as in {output_path}')