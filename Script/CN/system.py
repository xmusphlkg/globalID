
import os
from datetime import datetime
import yaml
import ast
from fun_getdata import *

# fetch data from setting
def fetch_data(existing_dates):
    """
    Fetch data from the sources specified in the environment variables. Using varied functions to get data from different sources.

    Args:
        existing_dates (list): A list of existing dates in the GetData folder.
    
    Returns:
        results (list): A list of dictionaries containing the data fetched from the sources.
        new_dates (list): A list of new dates that have been fetched.
        current_date (str): The current date in the format "YYYYMMDD".
    """
    sources = [
        {
            'active': os.environ['SOURCE_PUBMED_ACTIVE'],
            'label': os.environ['SOURCE_PUBMED_LABEL'],
            'url': os.environ['SOURCE_PUBMED_URL'],
            'origin': os.environ['SOURCE_PUBMED_ORIGIN'],
            'function': os.environ['SOURCE_PUBMED_FUNCTION'],
            'results': [],
            'new_dates': []
        },
        {
            'active': os.environ['SOURCE_CDC_ACTIVE'],
            'label': os.environ['SOURCE_CDC_LABEL'],
            'url': os.environ['SOURCE_CDC_URL'],
            'origin': os.environ['SOURCE_CDC_ORIGIN'],
            'function': os.environ['SOURCE_CDC_FUNCTION'],
            'results': [],
            'new_dates': []
        },
        {
            'active': os.environ['SOURCE_GOV_ACTIVE'],
            'label': os.environ['SOURCE_GOV_LABEL'],
            'url': os.environ['SOURCE_GOV_URL'],
            'origin': os.environ['SOURCE_GOV_ORIGIN'],
            'form_data': os.environ['SOURCE_GOV_DATA'],
            'function': os.environ['SOURCE_GOV_FUNCTION'],
            'results': [],
            'new_dates': []
        }
    ]

    for source in sources:
        active = source['active']
        label = source['label']
        if active == 'False':
            print(f"{label} is not active, try next one.")
            continue

        url = source['url']
        origin = source['origin']
        get_results = globals()[source['function']]

        if 'form_data' in source:
            form_data = ast.literal_eval(source['form_data'])
            results = get_results(url, form_data, label, origin)
        else:
            results = get_results(url, label, origin)

        new_dates = [result['YearMonth'] for result in results if result['YearMonth'] not in existing_dates and result['YearMonth'] not in source['new_dates']]
        if not new_dates:
            print(f"No new data in {label}, try next one.")
        else:
            source['results'] = [result for result in results if result['YearMonth'] in new_dates]
            source['new_dates'] = new_dates
            print(f"Find new data in {label}: {new_dates}")

    results = [result for source in sources for result in source['results']]
    new_dates = list(set([date for source in sources for date in source['new_dates']]))
    current_date = datetime.now().strftime("%Y%m%d")

    return results, new_dates, current_date

# get environment from config.yml
def load_env(file_path):
    """
    Load environment variables from a YAML file.

    Args:
        file_path (str): The path to the YAML configuration file.

    Raises:
        FileNotFoundError: If the YAML file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML file.
    """
    try:
        with open(file_path, 'r') as file:
            config_dict = yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing the YAML file: {e}")

    for section, subsections in config_dict.items():
        for key, subvalues in subsections.items():
            for subkey, value in subvalues.items():
                if isinstance(value, str):
                    env_var_name = f"{section.upper()}_{key.upper()}_{subkey.upper()}"
                    os.environ[env_var_name] = value
                    print(f"Set {env_var_name} = {value}")