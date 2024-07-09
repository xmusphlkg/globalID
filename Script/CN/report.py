import pandas as pd
import os
import shutil
import datetime
import logging
from jinja2 import Template
from pathlib import Path

from dataclean import calculate_change_data, format_table_data, generate_merge_chart
from mail import create_mail_table, generate_mail
from concurrent.futures import ThreadPoolExecutor, as_completed
from reportpage import create_report_page, create_report_summary
from reportfig import prepare_disease_data, plot_disease_data, plot_disease_heatmap
import variables

def process_plot(diseases_order, df):
    """
    Generate plotly figures for each disease.

    Args:
        diseases_order (list): the list of diseases
        df (dataframe): the dataframe

    Returns:
        list: the list of plotly figures
    """
    output = []
    for disease_name in diseases_order:
        disease_data = prepare_disease_data(df, disease_name)
        plot_html_1, plot_html_2 = plot_disease_data(disease_data, disease_name)
        plot_html_3, plot_html_4 = plot_disease_heatmap(disease_data, disease_name)
        output.append((disease_name, plot_html_1, plot_html_2, plot_html_3, plot_html_4))
    return output

def process_index(analysis_content, analysis_YearMonth, table_data, folder_path_web):
    
    datalink = os.environ["LINK_MAIN_SOURCE"]

    table_data['Diseases'] = table_data['Diseases'].apply(lambda x: f"[{x}](./{x.replace(' ', '-')})")
    table_of_content = table_data.to_markdown(index=False)

    with open(Path(__file__).parent / 'index.md', "r") as file:
        template = Template(file.read())

    filled_page = template.render(
        introduction=analysis_content,
        analysis_YearMonth=analysis_YearMonth,
        table=table_of_content,
        datalink=datalink
    )

    with open(os.path.join(folder_path_web, "-index.md"), "w") as file:
        file.write(filled_page)

    shutil.copyfile(os.path.join(folder_path_web, '-index.md'), os.path.join(folder_path_web, 'Total.md'))
    
def process_page(i, df, analysis_MonthYear, diseases_order, future_plot_dict, folder_path_web):
    introduction, highlights, caseanalysis, deathanalysis = create_report_page(df, diseases_order[i], analysis_MonthYear)
    plot_html_1, plot_html_2, plot_html_3, plot_html_4 = future_plot_dict[diseases_order[i]]
    datalink = os.environ["LINK_MAIN_SOURCE"]

    with open(Path(__file__).parent / 'page.md', "r") as file:
        template = Template(file.read())

    filled_page = template.render(
        disease_name=diseases_order[i],
        analysis_YearMonth=analysis_MonthYear,
        introduction=introduction,
        highlights=highlights,
        caseline=plot_html_1,
        caseheatmap=plot_html_3,
        caseanalysis=caseanalysis,
        deathline=plot_html_2,
        deathheatmap=plot_html_4,
        deathanalysis=deathanalysis,
        datalink=datalink
    )

    with open(os.path.join(folder_path_web, f"{diseases_order[i]}.md", "w")) as file:
        file.write(filled_page)

def generate_reports(analysis_YearMonth, folder_path_get, folder_path_save, folder_path_mail, folder_path_web):
    """
    Generate report for the given analysis_YearMonth

    Args:
        analysis_YearMonth (str): the analysis year and month
        data_path (dict): the path of data folder

    Returns:
        None    
    """
    # read data
    df = pd.read_csv(os.path.join(folder_path_save, 'latest.csv'))
    df['Date'] = pd.to_datetime(df['Date'])
    analysis_date = datetime.datetime.strptime(analysis_YearMonth + " 01", "%Y %B %d")
    analysis_MonthYear = analysis_date.strftime("%B %Y")
    
    # subset data
    date_range = variables.analysis_years
    start_date = analysis_date - pd.DateOffset(years=date_range)
    df = df[df['Date'] >= start_date]

    # calculate change data
    change_data = calculate_change_data(df, analysis_date)
    diseases_order, diseases_order_cn = generate_merge_chart(change_data, original_file=f'{folder_path_save}/{analysis_YearMonth}.csv')
    table_data = format_table_data(change_data, analysis_date)
    table_data['Diseases'] = pd.Categorical(table_data['Diseases'], categories=diseases_order + ['Total'], ordered=True)
    table_data = table_data.sort_values('Diseases')
    table_data = table_data.reset_index(drop=True)

    # create summary page
    df_10 = df[df['Date'] >= analysis_date - pd.DateOffset(years=5)]
    df_10 = df_10[['Date', 'YearMonth', 'Diseases', 'Cases', 'Deaths']]
    df_10 = df_10[df_10['Diseases'].isin(diseases_order)].sort_values(by=['Diseases', 'Date']).reset_index(drop=True)
    df_10['Values'] = df_10['Cases'].astype(str) + " (" + df_10['Deaths'].astype(str) + ")"
    df_10 = df_10.pivot(index='YearMonth', columns='Diseases', values='Values')
    table_data_str = df_10.to_markdown(index=False)
    
    # read legend
    with open(os.path.join(folder_path_get, 'latest.txt'), 'r') as f:
        table_legend = f.read()

    # create table
    table_of_content = table_data.to_markdown(index=False)
    create_mail_table(table_of_content, analysis_YearMonth, folder_path_mail)

    # create report page
    with ThreadPoolExecutor() as executor:
        # create figures
        future_plot = executor.submit(process_plot, diseases_order, df)
        # create cover and mail
        future_cover_mail = executor.submit(generate_mail, table_data_str, table_legend, analysis_YearMonth)
        # create summary
        future_report_summary = executor.submit(create_report_summary, table_data_str, analysis_MonthYear, table_legend)

        future_plot_dict = {disease_name: plots for disease_name, *plots in future_plot.result()}
        future_plot_dict_length = len(future_plot_dict)
        logging.info(f"Plots created for {analysis_YearMonth}, {future_plot_dict_length} diseases.")

        mail_content = future_cover_mail.result()
        with open(os.path.join(folder_path_mail, f'{analysis_YearMonth}_main.md'), 'w') as f:
            f.write(mail_content)
        shutil.copyfile(os.path.join(folder_path_mail, f'{analysis_YearMonth}_main.md'), os.path.join(folder_path_mail, 'latest_main.md'))
        logging.info(f"Mail content created for {analysis_YearMonth}.")

        analysis_content = future_report_summary.result()
        process_index(analysis_content, analysis_YearMonth, table_data, folder_path_web)
        logging.info(f"Summary page created for {analysis_YearMonth}.")

    with ThreadPoolExecutor(max_workers=len(diseases_order)) as executor:
        futures = [executor.submit(process_page, i, df, analysis_MonthYear, diseases_order, future_plot_dict, folder_path_web) for i in range(len(diseases_order))]

        # wait for all pages
        for future in as_completed(futures):
            page_result = future.result()
            logging.info(f"Processed report page {futures.index(future)} with result:", page_result)