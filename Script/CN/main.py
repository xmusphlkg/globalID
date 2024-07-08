
import re
import os
from datetime import datetime
import pandas as pd
import glob

from function import get_rss_results, get_gov_results, get_cdc_results, process_table_data
from analysis import generate_weekly_report
from sendmail import send_email_to_subscriber

# detect existing dates in GetData folder
folder_path = "./Data/GetData/CN/"
existing_dates = [os.path.splitext(file)[0] for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]

# Call the function to fetch data
results, new_dates, current_date = fetch_data(existing_dates)

if new_dates:
    print("Find new data, update.")
    print(results)

    # get data from url and save to WeeklyReport
    process_table_data(results)

    # access the folder
    csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]

    # read and merge CSV files
    merged_data = pd.DataFrame()
    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        data = pd.read_csv(file_path)
        merged_data = pd.concat([merged_data, data], ignore_index=True)

    merged_data = merged_data.sort_values(by=["Date", "Diseases"], ascending=False)
    first_row = merged_data.iloc[0]
    year_month = first_row["YearMonth"]
    merged_data = merged_data[['Date', 'YearMonthDay', 'YearMonth', 'Diseases', 'DiseasesCN', 'Cases', 'Deaths', 'Incidence', 'Mortality', 'ProvinceCN', 'Province', 'ADCode', 'DOI', 'URL', 'Source']]

    # get the unique values of diseases
    disease_unique = merged_data['Diseases'].unique()
    YearMonth_unique = merged_data['YearMonth'].unique()

    # save the merged data to a CSV file
    for YearMonth in YearMonth_unique:
        date_data = merged_data[merged_data['YearMonth'] == YearMonth]
        if date_data.empty:
            continue
        file_name = f'../CleanData/WeeklyReport/ALL/{YearMonth}.csv'
        date_data.to_csv(file_name, index=False, encoding="UTF-8-sig")

    # read all CSV files
    folder_path = '../CleanData/WeeklyReport/'
    csv_files = glob.glob(os.path.join(folder_path, '*/*.csv'))
    data = pd.concat([pd.read_csv(csv_file) for csv_file in csv_files], ignore_index=True)
    data = data.drop_duplicates()
    max_date = data['YearMonthDay'].max()
    max_date = datetime.strptime(max_date, '%Y/%m/%d').strftime("%Y %B")
    data.to_csv('..' + '/AllData/WeeklyReport/latest.csv', index=False, encoding='utf-8', header=True)
    data.to_csv('..' + '/AllData/WeeklyReport/' + max_date + '.csv', index=False, encoding='utf-8', header=True)

    # modify the markdown file
    readme_path = "../../Readme.md"
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
    os.chdir("../../Script")
    for YearMonth in new_dates:
        print("Generate report for " + YearMonth)
        generate_weekly_report(YearMonth)
    if send_mail == 'True':
        send_email_to_subscriber(test_mail)

    # print success message
    print("Data updated successfully!")
else:
    print("No new data, stop.")