
import re
import os
from datetime import datetime
import pandas as pd
import glob
import shutil
import logging

from system import get_sources
from dataget import fetch_data, process_table_data
from report import generate_reports
from sendmail import send_email_to_subscriber

# set up folder paths
folder_path_get = "../../Data/GetData/CN/"
folder_path_save = "../../Data/AllData/CN/"
folder_path_mail = "../../Mail/CN/"
folder_path_web = "../../Website/content/CN"
folder_path_log = "../../Log/CN"

# load environment variables
env_path = os.path.join(os.path.dirname(__file__), 'config.yml')
sources = get_sources(env_path)

# detect existing dates in GetData folder
existing_dates = [os.path.splitext(file)[0] for file in os.listdir(folder_path_get) if os.path.isfile(os.path.join(folder_path_get, file))]

# Call the function to fetch data
results, new_dates, current_date = fetch_data(sources, existing_dates)

if new_dates:
    # get data from url and save to GetData folder
    process_table_data(results, folder_path_get)

    # access the folder
    csv_files = [file for file in os.listdir(folder_path_get) if file.endswith(".csv")]

    # read and merge CSV files
    merged_data = pd.DataFrame()
    for file in csv_files:
        file_path = os.path.join(folder_path_get, file)
        data = pd.read_csv(file_path)
        merged_data = pd.concat([merged_data, data], ignore_index=True)

    merged_data = merged_data.sort_values(by=["Date", "Diseases"], ascending=False)
    first_row = merged_data.iloc[0]
    year_month = first_row["YearMonth"]
    merged_data = merged_data[['Date', 'YearMonthDay', 'YearMonth', 'Diseases', 'DiseasesCN', 'Cases', 'Deaths', 'Incidence', 'Mortality', 'ProvinceCN', 'Province', 'ADCode', 'DOI', 'URL', 'Source']]

    # get the unique values of diseases
    disease_unique = merged_data['Diseases'].unique()
    YearMonth_unique = merged_data['YearMonth'].unique()

    # update all data
    csv_files = glob.glob(os.path.join(folder_path_get, '*.csv'))
    data = pd.concat([pd.read_csv(csv_file) for csv_file in csv_files], ignore_index=True)
    data = data.drop_duplicates()
    max_date = data['YearMonthDay'].max()
    max_date = datetime.strptime(max_date, '%Y/%m/%d').strftime("%Y %B")
    data.to_csv(os.path.join(folder_path_save, max_date + '.csv'), index=False, encoding='utf-8', header=True)
    shutil.copyfile(os.path.join(folder_path_save, max_date + '.csv'), os.path.join(folder_path_save, 'latest.csv'))

    # modify the markdown file
    readme_path = os.path.join(folder_path_log, "README.md")
    with open(readme_path, "r", encoding='utf-8') as readme_file:
        readme_content = readme_file.read()
    update_log = f"#### {year_month}\n\nDate: {current_date}\n\nUpdated: {new_dates}\n\n"
    pattern = re.compile(rf"#### {re.escape(year_month)}.*?(?=####|$)", re.DOTALL)
    if re.search(pattern, readme_content):
        updated_readme_content = re.sub(pattern, update_log, readme_content)
    else:
        updated_readme_content = readme_content.replace("### China CDC Monthly Report", "### China CDC Monthly Report\n\n" + update_log)
    with open(readme_path, "w") as readme_file:
        readme_file.write(updated_readme_content)
    
    test_mail = os.environ['test_mail']
    send_mail = os.environ['send_mail']
    # change working directory
    for YearMonth in new_dates:
        # set up logging
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            filename=os.path.join(folder_path_log, YearMonth + '.log'),
                            filemode='w')
        logging.info(f"Start processing {YearMonth} data...")
        generate_reports(YearMonth, folder_path_get, folder_path_save, folder_path_mail, folder_path_web)
    if send_mail == 'True':
        send_email_to_subscriber(test_mail)

    # print success message
    logging.info(f"Data processing completed for {new_dates}.")
else:
    print("No new data, stop.")