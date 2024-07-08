import os
import yaml
import ast

def set_env_vars(config):
    """
    Set environment variables for configurations that are not part of the data sources.
    
    Args:
        config (dict): Configuration dictionary loaded from YAML.
    """
    for section, settings in config.items():
        if section != 'Source':  # Ignore the data source section
            for key, value in settings.items():
                for subkey, subvalue in value.items():
                    env_var_name = f"{section.upper()}_{key.upper()}_{subkey.upper()}"
                    os.environ[env_var_name] = str(subvalue)
                    print(f"Set {env_var_name} = {subvalue}")

def load_config(file_path):
    """
    Load configuration settings from a YAML file.
    
    Args:
        file_path (str): The path to the YAML configuration file.
    
    Returns:
        dict: A dictionary containing the loaded configuration settings.
    
    Raises:
        FileNotFoundError: If the YAML file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML file.
    """
    try:
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    except yaml.YAMLError as e:
        raise Exception(f"Error parsing the YAML file: {e}")
    
    # set environment variables
    set_env_vars(config)

    return config

def get_sources(file_path):
    """
    Format and extract data sources from the configuration.
    
    Args:
        config (dict): Configuration dictionary loaded from YAML.
    
    Returns:
        list: A list of formatted source dictionaries.
    """
    config = load_config(file_path)

    sources = []
    for key, value in config['Source'].items():
        source = {
            'active': value['Active'] == 'True',
            'label': value['Label'],
            'url': value['Url'],
            'origin': value['Origin'],
            'function': value['Function']
        }
        if 'Data' in value:
            source['form_data'] = ast.literal_eval(value['Data'])
        sources.append(source)
    return sources
