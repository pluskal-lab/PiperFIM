from pathlib import Path
import pandas as pd
import numpy as np
from src.utils import load_config

#load config file
config = load_config(path='config/config.yaml', section='lc-ms')

### Sample list ###
metadata = pd.read_csv(config['metadata'], sep='\t')
filenames = metadata['filename']
sample_rep_names = metadata['ATTRIBUTE_Replicate']


### MZmine ###
ftable = pd.read_csv(config['ftable'])
ftable.columns = [col.replace(' Peak area', '') if ' Peak area' in col else col for col in ftable.columns] #remove 'Peak area' from sample columns
ftable = ftable[['row ID', 'row m/z', 'row retention time', 'correlation group ID', 'best ion', 'neutral M mass'] + filenames.tolist()] #keep relevant columns
rename_map = dict(zip(filenames, sample_rep_names)) #rename sample columns
rename_map.update({'row ID': 'feat_ID',
                'row m/z': 'mz',
                'row retention time': 'RT',
                'correlation group ID': 'corrGroup_ID',
                'best ion':'adduct',
                'neutral M mass': 'neutral mass'}) #rename ID columns
ftable.rename(columns=rename_map, inplace=True)

#create `corrGroup_size` column
corrGroup_size = ftable.groupby('corrGroup_ID')['corrGroup_ID'].count() #count features in corrGroups
ftable = ftable.merge(corrGroup_size, how='left', left_on ='corrGroup_ID', right_index=True, suffixes = (None, '_size'))
ftable.insert(4, 'corrGroup_size', ftable.pop('corrGroup_ID_size')) #change column order

#calculate average of replicates
ftable.set_index('feat_ID', inplace=True)
peak_areas = ftable.loc[:, sample_rep_names].T #peak area columns, featrures in rows
peak_areas['sample-tissue'] = [name.rsplit('-', 1)[0] for name in peak_areas.index] #create 'sample-tissue' columns for grouby
peak_areas = peak_areas.groupby('sample-tissue', sort=False).mean().T #calculate mean, featrures in columns
ftable.drop(columns=sample_rep_names, inplace=True) #drop original columns
ftable = ftable.merge(peak_areas, how='left', left_index=True, right_index=True) #merge average peak areas back to ftable

#import localDB annotations
annotations = pd.read_csv(config['annotations'], usecols=['id', 'compound_name'], na_values='')
annotations.rename(columns={'id': 'feat_ID',
                            'compound_name': 'customDB'}, inplace=True)
annotations.set_index('feat_ID', inplace=True)
ftable = ftable.merge(annotations, how='left', left_index=True, right_index=True) #create 'customDB' column


### SIRIUS ###
#CSI:FingerID
fingerid = pd.read_csv(config['fingerid'], sep='\t', usecols= ['smiles', 'name', 'CSI:FingerIDScore', 'ConfidenceScore', 'molecularFormula', 'featureId'])
fingerid.rename(columns={'name': 'FingerID_name',
                        'ConfidenceScore':'COSMIC_score',
                        'CSI:FingerIDScore':'FingerID_score',
                        'smiles': 'FingerID_smiles',
                        'molecularFormula':'FingerID_formula',
                        'featureId':'feat_ID'}, inplace=True)
fingerid.set_index('feat_ID', inplace=True)

#CANOPUS
canopus = pd.read_csv(config['canopus'], sep='\t', usecols= ['NPC#pathway', 'NPC#pathway Probability', 'NPC#superclass', 'NPC#superclass Probability', 'NPC#class', 'NPC#class Probability', 'molecularFormula', 'featureId'])
canopus.rename(columns={'NPC#pathway':'NPCpathway',
                        'NPC#pathway Probability':'NPCpathway_score',
                        'NPC#superclass':'NPCsuperclass',
                        'NPC#superclass Probability':'NPCsuperclass_score',
                        'NPC#class':'NPCclass',
                        'NPC#class Probability':'NPCclass_score',
                        'molecularFormula':'CANOPUSformula',
                        'featureId':'feat_ID'}, inplace=True)
canopus.set_index('feat_ID', inplace=True)


### GNPS2 node table ###
gnps = pd.read_csv(config['gnps2_ntable'], sep='\t', usecols=['cluster index', 'parent mass', 'RTMean', 'component'])
gnps.rename(columns={'cluster index': 'feat_ID',
                'parent mass': 'mz',
                'RTMean': 'RT',
                'component': 'network_ID'}, inplace=True) #rename columns
gnps['mz'] = gnps['mz'].round(4) #round m/z to 4 decimals
gnps['RT'] = gnps['RT'].round(2) #round RT to 2 decimals

#create 'network_size' column
network_size = gnps.groupby('network_ID')['network_ID'].count()
gnps = gnps.merge(network_size, how='left', left_on ='network_ID', right_index=True, suffixes = (None, '_count')).rename(columns={'network_ID_count': 
'network_size'}) 
gnps.set_index('feat_ID', inplace=True)

#merge peak areas from MZmine feature table
sample_tissue_names = metadata['ATTRIBUTE_Tissue'].drop_duplicates() 
gnps = gnps.merge(ftable[sample_tissue_names], how='left', left_index=True, right_index=True) #merge CSI:FingerID annotations

#create 'Log2_intensity' column (using ATTRIBUTE_Replicate columns)
gnps['Log2(sum-intensity)'] = np.log2(gnps[sample_tissue_names].sum(axis=1))
gnps['Log2(sum-intensity)'] = gnps['Log2(sum-intensity)'].replace(-np.inf, 0) #replace -inf with 0

#library matches
mslib = pd.read_csv(config['gnps2_lib'], sep='\t', usecols=['#Scan#', 'Compound_Name', 'LibMZ', 'MassDiff', 'MQScore', 'Smiles', 'Instrument'])
mslib.rename(columns={'#Scan#': 'feat_ID',
                'Compound_Name': 'GNPSLib_name',
                'LibMZ': 'GNPSLib_mz',
                'MassDiff': 'GNPSLib_MassDiff',
                'MQScore': 'GNPSLib_score',
                'Instrument': 'GNPSLib_instrument',
                'Smiles': 'GNPSLib_smiles'}, inplace=True) #rename columns
mslib.set_index('feat_ID', inplace=True)


### Merge and Export ###
#MZmine feateure table
ftable = ftable.merge(canopus, how='left', left_index=True, right_index=True)
ftable = ftable.merge(fingerid, how='left', left_index=True, right_index=True)
ftable = ftable.merge(mslib, how='left', left_index=True, right_index=True)
ftable = ftable.merge(gnps[['network_ID', 'network_size']], how='left', left_index=True, right_index=True)
ftable.to_csv(config['ftable_clean'])

#GNPS node table
gnps = gnps.merge(ftable[['adduct', 'neutral mass', 'customDB', 'corrGroup_ID']], how='left', left_index=True, right_index=True)
gnps = gnps.merge(canopus, how='left', left_index=True, right_index=True)
gnps = gnps.merge(fingerid, how='left', left_index=True, right_index=True)
gnps = gnps.merge(mslib, how='left', left_index=True, right_index=True) #merge library matches to node table
gnps.to_csv(config['ntable_clean'])