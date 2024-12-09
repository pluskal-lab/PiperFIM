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

#import Angiosperms tree
tree_file_path = Path(config['tree_file'])
tree = Phylo.read(tree_file_path, 'newick')
logging.info(f'Angiosperms phylogenetic tree successfully imported!')
tree_leaves = [leaf.name for leaf in tree.get_terminals()] #extract leaf names
tree_leaves = pd.Series(tree_leaves, name='leaf_name')
logging.info(f'Tree contains {len(tree_leaves)} leaves')
logging.info(f"{tree_leaves.str.endswith('sp.').sum()} species names are not defined in the tree (e.g., 'Lessertia_sp.')")

#import scaffold list
scaffold_list = config['scaffolds']

#import cleaned sparql results, concatenate into single df
scaffold_df = []
for scaffold, path in config['sparql_results_clean'].items():
    df = pd.read_csv(path)
    df['Scaffold'] = scaffold
    scaffold_df.append(df)
scaffold_df = pd.concat(scaffold_df, ignore_index=True)


#convert tree into df with order, family, genus, species
tree_df = tree_leaves.str.split('_', expand=True)
tree_df = tree_df.iloc[:, :4] #keep first 4 columns
tree_df.columns = ['Order', 'Family', 'Genus', 'Species']
tree_df = pd.concat([tree_leaves, tree_df], axis=1).rename(columns={0: 'leaf_name'}).set_index('leaf_name')

#add binary column for each scaffold (0: not reported; 1:reported)
for s in scaffold_list:
    tree_df[s] = 0  #create zero column
    genera_list = scaffold_df[scaffold_df['Scaffold'] == s]['genus_name'].unique() #list of genera with report (for each scaffold)

    #if genus with report present in the tree, set to 1
    for g in genera_list:
        tree_df.loc[tree_df['Genus'] == g, s] = 1


#add seco-bia scaffold in Piper (result from present study) and Antidesma genera 
tree_df.loc['Piperales_Piperaceae_Piper_nigrum', 'seco-bia'] = 1
tree_df.loc['Malpighiales_Phyllanthaceae_Antidesma_bunius', 'seco-bia'] = 1
logging.info(f"seco-bia scaffold set as 'reported' in Piper genus (based on the present study)!")


#create iTOL binary datasets
itol = tree_df[['benzylisoquinoline', 'aporphine', 'piperolactam', 'piperidine', 'seco-bia']] #reorder columns
itol = itol.replace(0, -1) #replace 0 with -1

#write iTOL annotation file
output_path = Path('results/phylo_tree/iTOL_scaffolds.txt')
with open(output_path, 'w') as f: 
    #write headers
    f.write('DATASET_BINARY\n')
    f.write('SEPARATOR COMMA\n')
    f.write(f'DATASET_LABEL,Scaffold\n') #dataset name
    f.write(f'COLOR,{",".join(["#000000"] * len(itol.columns))}\n') #all black
    f.write(f'FIELD_SHAPES,{",".join([str(i + 1) for i in range(len(itol.columns))])}\n') #shapes from 1 to 5
    f.write(f'FIELD_LABELS,{",".join(itol.columns)}\n') #scaffold names
    f.write('DATA\n')

    #write dataset
    for id, row in itol.iterrows():
        f.write(f'{id},{",".join(map(str, row.values))}\n') #convert row values to strings and join them with commas

    logging.info(f'iTOL annotation file written to {output_path}')