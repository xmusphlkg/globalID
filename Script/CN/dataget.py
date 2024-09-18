
import requests
import xmltodict
from requests.exceptions import RequestException
import re
from bs4 import BeautifulSoup
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
import json
from urllib.parse import urljoin
from reporttext import openai_trans

# define a function to extract date from text
def extract_date(text):
    """
    Extract the date from a text string, English version.

    Args:
        text (str): A text string containing the date, such as "Weekly Epidemiological Update - 1 June 2021".

    Returns:
        str: The extracted date in the format "YYYY Month", such as "2021 June".
    """
    text_without_tags = re.sub(r"<[^>]+>", "", text)
    text_without_special_chars = re.sub(r"[^a-zA-Z0-9\s]", "", text_without_tags)
    match = re.search(r"\b([A-Za-z]+)\s+(\d{4})\b", text_without_special_chars)
    if match:
          return(match.group(2) + " " + match.group(1))
    else:
          return(None)

def extract_date_cn(text):
    """
    Extract the date from a text string, Chinese version.

    Args:
        text (str): A text string containing the date, such as "2021年6月".

    Returns:
        str: The extracted date in the format "YYYY Month", such as "2021 June".
    """

    text_without_tags = re.sub(r"<[^>]+>", "", text)
    text_without_special_chars = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fa5\s]", "", text_without_tags)
    match = re.search(r"(\d{4})年(\d{1,2})月", text_without_special_chars)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        date_obj = datetime(year, month, 1)
        formatted_date = date_obj.strftime("%Y %B")
        return formatted_date
    else:
        return None
    
def find_max_date(YearMonths):
    """
    Find the maximum date from a list of dates in the format "YYYY Month".

    Args:
        YearMonths (list): A list of dates in the format "YYYY Month".

    Returns:
        str: The maximum date in the format "YYYY Month", such as "2021 June".
    """
    date_objects = [datetime.strptime(date, "%Y %B") for date in YearMonths]
    max_date = max(date_objects, key=lambda x: x)
    max_date_str = max_date.strftime("%Y %B")
    return max_date_str

# define a function to get PubMed RSS results
def get_rss_results(url, label, origin):
    """
    Get the latest results from a PubMed RSS feed.

    Args:
        url (str): The URL of the PubMed RSS feed.
        label (str): The label for the source of the results.
        origin (str): The origin of the results.

    Raises:
        Exception: If there are no items found in the RSS feed.

    Returns:
        list: A list of dictionaries containing the extracted information.    
    """
    # Send request and get response
    try:
        response = requests.get(url)
        response.raise_for_status()
    except RequestException as e:
        raise Exception(f"Failed to fetch {label} results from {url}. Error: {e}")

    # Parse XML results
    try:
        rss_results = xmltodict.parse(response.content)
        items = rss_results.get("rss", {}).get("channel", {}).get("item", [])
    except Exception as e:
        raise Exception(f"Error parsing XML from {url}. Error: {e}")
    
    if not items:
        raise Exception(f"No items found in RSS feed from {url}.")

    # Extract results
    results = []
    for item in rss_results["rss"]["channel"]["item"]:
        date = extract_date(item["title"])
        # Skip if the date is not extracted
        if not date:
            continue

        # Append the extracted information to the results list
        date_obj = datetime.strptime(date, "%Y %B")
        formatted_date = date_obj.strftime("%Y/%m/%d")
        results.append({
            "title": item["title"],
            "pubDate": item["pubDate"],
            "dc:date": item["dc:date"],
            "date": date_obj,
            "YearMonthDay": formatted_date,
            "YearMonth": date,
            "doi": item["dc:identifier"],
            "source": label,
            "origin": origin
        })

    # Sort by date
    results.sort(key=lambda result: result["date"], reverse=False)
    # Exclude the first 4 results
    results = results[4:]

    return results


# define a function to get china cdc weekly results
def get_cdc_results(url, label, origin):
    """
    Get the latest results from the China CDC Weekly.

    Args:
        url (str): The URL of the China CDC Weekly.
        label (str): The label for the source of the results.
        origin (str): The origin of the results.

    Raises:
        Exception: If there are no <a> tags found in the HTML content.

    Returns:
        list: A list of dictionaries containing the extracted information.    
    """
    # Send an HTTP request to get the webpage content
    try:
        response = requests.get(url)
        response.raise_for_status()
    except RequestException as e:
        raise Exception(f"Failed to fetch {label} results from {url}. Error: {e}")

    # Parse HTML results
    try:
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        a_tags = soup.find_all("a")
    except Exception as e:
        raise Exception(f"Error parsing HTML from {url}. Error: {e}")
    
    # Extract results
    if not a_tags:
        raise Exception(f"No <a> tags found in HTML content from {url}.")

    # Traverse each <a> tag, extract text and link
    result_list = []
    for a_tag in a_tags:
        text = a_tag.text.strip()
        link = a_tag.get("href")
        if link and "doi" in link and "National Notifiable Infectious Diseases" in text:
            date = extract_date(re.sub(r"[^\w\s-]", "", text))
            date_obj = datetime.strptime(date, "%Y %B")
            formatted_date = date_obj.strftime("%Y/%m/%d")
            doi = link.split("doi/")[1]
            result_list.append({
                "title": text,
                "date": date_obj,
                "YearMonthDay": formatted_date,
                "YearMonth": date,
                "link": url + link,
                "doi": ['missing', 'missing', 'doi:' + doi],
                "source": label,
                "origin": origin
            })

    result_list = list({v['link']: v for v in result_list}.values())
    return result_list

def get_gov_results(url, form_data, label, origin):
    """
    Get the latest results from a government website.

    Args:
        url (str): The URL of the government website.
        form_data (dict): The form data to be sent in the POST request.
        label (str): The label for the source of the results.
        origin (str): The origin of the results.

    Raises:
        Exception: If there are no results returned from the government website.

    Returns:
        list: A list of dictionaries containing the extracted information.
    """
    # Send a request and get the response
    try:
        response = requests.post(url, data=form_data)
        response.raise_for_status()
    except RequestException as e:
        raise Exception(f"Failed to fetch {label} results from {url}. Error: {e}")
    
    # Parse JSON results
    try:
        titles = [response.json()['data']['results'][i]['source']['title'] for i in range(10)]
        links = [response.json()['data']['results'][i]['source']['urls'] for i in range(10)]
    except Exception as e:
        raise Exception(f"Error parsing JSON from {url}. Error: {e}")
    
    # Check if the response contains data
    if len(response.json()['data']['results']) == 0:
        raise Exception(f"Failed to fetch {label} results. No data returned.")

    # Traverse each <a> tag, extract text and link
    result_list = []
    for title,link in zip(titles,links):
        if title and link:
            date = extract_date_cn(title)
            # Skip if the date is not extracted
            if not date:
                continue

            # Append the extracted information to the results list
            date_obj = datetime.strptime(date, "%Y %B")
            formatted_date = date_obj.strftime("%Y/%m/%d")
            link = json.loads(link).get('common')
            link = urljoin(url, link)
            result_list.append({
                "title": title,
                "date": date_obj,
                "YearMonthDay": formatted_date,
                "YearMonth": date,
                "link": link,
                "doi": ['missing', 'missing', 'missing'],
                "source": label,
                "origin": origin
            })
    return result_list

# define a function to get table data from URLs
def is_column_meaningful(column):
    """
    Check if a pandas Series contains meaningful data.

    Args:
        column (pandas.Series): A pandas Series representing a column in a table.

    Returns:
        bool: True if the column contains meaningful data, False otherwise.
    """
    non_empty_rows = column[column != ""].count()
    return non_empty_rows / len(column) > 0.1

# define a function to get table data from URLs
def get_table_data(url):
    """
    Get table data from a URL.

    Args:
        url (str): The URL of the webpage containing the table data.

    Raises:
        Exception: If the HTTP response status code is not 200.

    Returns:
        pandas.DataFrame: A DataFrame containing the table data.
    """
    # Send a request and get the response
    try:
        response = requests.get(url)
        response.raise_for_status()
        print("Successfully fetched web content, urls: {}".format(url))
    except RequestException as e:
        raise Exception(f"Failed to fetch web content from {url}. Error: {e}")
    
    # Use pandas to directly parse the table data
    try:
        text = response.text
        soup = BeautifulSoup(text, 'html.parser')
        tables = soup.find_all('table')[0]
    except Exception as e:
        raise Exception(f"Error parsing HTML table from {url}. Error: {e}")
    
    # Check if the table contains data
    if len(tables) == 0:
        raise Exception(f"No tables found in HTML content from {url}.")
    
    # Extract the table data
    data = []
    thead = tables.find('thead')
    if thead:
        thead_rows = thead.find_all('tr')
        for tr in thead_rows:
            data.append([th.get_text().strip() for th in tr.find_all(['td', 'th'])])

    table_body = tables.find('tbody')
    if table_body:
        rows = table_body.find_all('tr')
        for tr in rows:
            cells = tr.find_all('td')
            if cells:
                data.append([td.get_text().strip() for td in cells])

    table_data = pd.DataFrame(data)
    for column in table_data:
      if not is_column_meaningful(table_data[column]):
          table_data.drop(column, axis=1, inplace=True)

    return table_data

def clean_table_data(data, filtered_result, Code2Name):
    """
    Clean the table data and add additional columns.

    Args:
        data (pandas.DataFrame): A DataFrame containing the table data.
        filtered_result (dict): A dictionary containing the extracted information.
        Code2Name (dict): A dictionary mapping disease codes to disease names.

    Returns:
        pandas.DataFrame: A cleaned DataFrame containing the table data.
    
    """
    # Clean database
    data = data.iloc[1:].copy()
    data.columns = ['Diseases', 'Cases', 'Deaths']
    data['Diseases'] = data['Diseases'].str.replace(r"[^\w\s]", "", regex=True)

    # Add various columns
    column_names = ['DOI', 'URL',
                    'Date', 'YearMonthDay', 'YearMonth',
                    'Source',
                    'Province', 'ProvinceCN', 'ADCode',
                    'Incidence', 'Mortality']
    column_values = [filtered_result['doi'][2], filtered_result['link'],
                     filtered_result["date"], filtered_result["YearMonthDay"], filtered_result["YearMonth"],
                     filtered_result["source"], 'China', '全国', '100000', -10, -10]

    for name, value in zip(column_names, column_values):
        data[name] = value
    
    # trans Diseases to DiseasesCN
    diseaseCode2Name = pd.read_csv(Code2Name)
    diseaseCode2Name = dict(zip(diseaseCode2Name["Code"], diseaseCode2Name["Name"]))
    data['DiseasesCN'] = data['Diseases'].map(diseaseCode2Name)

    # Reorder the column names
    column_order = ['Date', 'YearMonthDay', 'YearMonth', 'Diseases', 'DiseasesCN', 'Cases', 'Deaths', 'Incidence', 'Mortality', 'ProvinceCN', 'Province', 'ADCode', 'DOI', 'URL', 'Source']
    table_data = data[column_order]

    return table_data

def clean_table_data_cn(data, filtered_result, Name2Code):
    """
    Clean the table data and add additional columns.

    Args:
        data (pandas.DataFrame): A DataFrame containing the table data.
        filtered_result (dict): A dictionary containing the extracted information.
        Name2Code (dict): A dictionary mapping disease names to disease codes.

    Returns:
        pandas.DataFrame: A cleaned DataFrame containing the table data.    
    """
    # Clean database
    data = data.iloc[1:].copy()
    data.columns = ['DiseasesCN', 'Cases', 'Deaths']
    data = data[~data['DiseasesCN'].str.contains('合计')]
    data['DiseasesCN'] = data['DiseasesCN'].str.replace(r"[^\w\s\u4e00-\u9fa5]", "", regex=True)
    data['DiseasesCN'] = data['DiseasesCN'].str.replace(r"甲乙丙类总计", "合计", regex=True)
    
    # Add various columns
    column_names = ['DOI', 'URL',
                    'Date', 'YearMonthDay', 'YearMonth',
                    'Source',
                    'Province', 'ProvinceCN', 'ADCode',
                    'Incidence', 'Mortality']
    column_values = [filtered_result["doi"][2], filtered_result['link'],
                     filtered_result["date"], filtered_result["YearMonthDay"], filtered_result["YearMonth"],
                     filtered_result["source"],
                     'China', '全国', '100000',
                     -10, -10]
    for name, value in zip(column_names, column_values):
        data[name] = value
    
    # trans DiseasesCN to Diseases
    diseaseName2Code_df = pd.read_csv(Name2Code)
    diseaseName2Code = dict(zip(diseaseName2Code_df["Name"], diseaseName2Code_df["Code"]))
    data['Diseases'] = data['DiseasesCN'].map(diseaseName2Code)
    
    na_indices = data['DiseasesCN'][data['DiseasesCN'].isna()].index
    for i in na_indices:
        data.loc[i, 'Diseases'] = openai_trans(os.environ["DATA_TRANSLATE_CREATE"],
                                               os.environ["DATA_TRANSLATE_CHECK"],
                                               data.loc[i, 'DiseasesCN'],
                                               diseaseName2Code.values())
        # append the new translation to diseaseName2Code_df
        diseaseName2Code_df = diseaseName2Code_df.append({'Name': data.loc[i, 'DiseasesCN'], 'Code': data.loc[i, 'Diseases']},
                                                         ignore_index=True)
    
    # if update diseaseName2Code.csv
    if len(na_indices) > 0:
        diseaseName2Code_df.to_csv(Name2Code, index=False)

    # Reorder the column names
    column_order = ['Date', 'YearMonthDay', 'YearMonth', 'Diseases', 'DiseasesCN', 'Cases', 'Deaths', 'Incidence', 'Mortality', 'ProvinceCN', 'Province', 'ADCode', 'DOI', 'URL', 'Source']
    table_data = data[column_order]

    return table_data

def process_table_data(results, path):
    """
    Process table data from URLs and save the results to CSV files.

    Args:
        results (list): A list of dictionaries containing the extracted information.

    Raises:
        Exception: If the HTTP response status code is not 200.

    Returns:
        None
    """
    urls = [result['link'] for result in results]

    for i, url in enumerate(urls):
        # Send a request and get the response
        origin = results[i]['origin']
        data_raw = get_table_data(url)
        
        if origin == 'CN':
            data = clean_table_data_cn(data_raw,
                                       results[i],
                                       Path(__file__).parent / 'variables' / 'diseaseName2Code.csv')
        else:
            data = clean_table_data(data_raw,
                                    results[i],
                                    Path(__file__).parent / 'variables' / 'diseaseCode2Name.csv')

        # Save the results for each month to a CSV file
        file_name = os.path.join(path, results[i]["YearMonth"] + ".csv")
        data.to_csv(file_name, index=False, encoding="UTF-8-sig")


def fetch_data(sources, existing_dates):
    """
    Fetch data from sources specified in the provided configuration.
    
    Args:
        sources (list): A list of source configurations.
        existing_dates (list): A list of existing dates in the GetData folder.
    
    Returns:
        tuple: Contains a list of fetched data results, new dates, and the current date.
    """
    results = []
    new_dates = set()
    for source in sources:
        if not source['active']:
            print(f"{source['label']} is not active, try next one.")
            continue
        
        get_results = globals()[source['function']]
        kwargs = {'url': source['url'], 'label': source['label'], 'origin': source['origin']}
        if 'form_data' in source:
            kwargs['form_data'] = source['form_data']
        
        source_results = get_results(**kwargs)
        source_new_dates = [result['YearMonth'] for result in source_results 
                            if result['YearMonth'] not in existing_dates]
        if source_new_dates:
            results.extend([result for result in source_results if result['YearMonth'] in source_new_dates])
            new_dates.update(source_new_dates)
            print(f"Find new data in {source['label']}: {source_new_dates}")
        else:
            print(f"No new data in {source['label']}, try next one.")

    current_date = datetime.now().strftime("%Y%m%d")
    return results, list(new_dates), current_date