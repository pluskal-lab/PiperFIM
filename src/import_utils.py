
import pandas as pd
import yaml
from pathlib import Path


########## Load config.yaml files ##########
def read_config(config_path: str, filepaths: bool=True, **kwargs):
    """
    Load a config.yaml file as dictionary.

    Parameters:
    config_path (str): path to the YAML configuration file.
    filepaths (bool): if True, convert all string values to Path objects.
    **kwargs: keyword arguments representing keys in the YAML file.

    Returns:
    dict: config.yaml file as dictionary.

    Raises:
    KeyError: if one of the keys in kwargs is not found in the config.yaml.
    """

    #load config.yaml as dict
    with open(config_path, "r") as handle:
        config = yaml.safe_load(handle)
    
    #keep portion of config.yaml based on provided keys 
    try:
        for argument, value in kwargs.items(): #iterates over config levels provided in kwargs"
            if value not in config: #if one of the provided levels is not in the config.yaml, raise error.
                raise KeyError(f'Key {value} not found in the config.yaml') 
            if isinstance(config[value], str): #if config[value] is a string, return it and end the loop
                return config[value]
            else: #if config[value] is not a string (i.e., it's still a dict), update config to be the nested dict and go to next iteration
                config = config[value]
        
        #convert str paths to Path objects
        if filepaths:
            config = {k: Path(v) if isinstance(v, str) else v for k, v in config.items()}
    
        return config
    
    except KeyError as e:
        raise KeyError(str(e))
    



########## Import SonicParanoid output ##########
def import_sonicpd(file_path):
    sonicpd = pd.read_csv(file_path, sep='\t', index_col='group_id')
    sonicpd = sonicpd.applymap(lambda x: x.split(',') if isinstance(x, str) else x) #turn entries into lists (instead of strings)
    sonicpd = sonicpd.applymap(lambda x: [] if x == ['*'] else x) #replace empty entries with empty lists instead of '*' 
    sonicpd.columns = [col.split('.')[0] for col in sonicpd.columns] #remove .pep from col names
    return sonicpd