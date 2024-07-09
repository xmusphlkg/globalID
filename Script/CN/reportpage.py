
import os
import variables

from reportfig import prepare_disease_data
from reporttext import openai_single, openai_abstract

def create_report_page(disease_name,
                       df,
                       report_date):
    """
    This function is used to process disease data.

    Args:
        disease_name (str): the disease name
        df (dataframe): the data
        report_date (str): the report date

    Returns:

    """
    # prepare data
    disease_data = prepare_disease_data(df, disease_name)
    table_data_str = disease_data[['YearMonth', 'Cases', 'Deaths']].to_markdown(index=False)

    introduction_box_content = openai_single(
        os.environ['REPORT_INTRODUCTION_CREATE'],
        os.environ['REPORT_INTRODUCTION_CHECK'],
        variables.introduction_create.format(disease_name=disease_name), 
        variables.introduction_check.format(disease_name=disease_name),
        variables.introduction_words,
        "Introduction",
        disease_name
        )

    highlights_box_content = openai_single(
        os.environ['REPORT_HIGHLIGHTS_CREATE'],
        os.environ['REPORT_HIGHLIGHTS_CHECK'],
        variables.highlights_create.format(disease_name=disease_name, report_date=report_date, table_data_str=table_data_str),
        variables.highlights_check.format(disease_name=disease_name),
        variables.highlights_words,
        "Highlights",
        disease_name
        )

    cases_box_content = openai_single(
        os.environ['REPORT_CASEANALYSIS_CREATE'],
        os.environ['REPORT_CASEANALYSIS_CHECK'],
        variables.caseanalysis_create.format(disease_name=disease_name, table_data_str=table_data_str),
        variables.caseanalysis_check.format(disease_name=disease_name),
        variables.caseanalysis_words,
        "Cases Analysis",
        disease_name
        )
    
    deaths_box_content = openai_single(
        os.environ['REPORT_DEATHANALYSIS_CREATE'],
        os.environ['REPORT_DEATHANALYSIS_CHECK'],
        variables.deathanalysis_create.format(disease_name=disease_name, table_data_str=table_data_str),
        variables.deathanalysis_check.format(disease_name=disease_name),
        variables.deathanalysis_words,
        "Deaths Analysis",
        disease_name
        )
    
    return introduction_box_content, highlights_box_content, cases_box_content, deaths_box_content

def create_report_summary(table_data_str, analysis_MonthYear, legend):
    analysis_content = openai_abstract(os.environ['REPORT_ABSTRACT_CREATE'],
                                       os.environ['REPORT_ABSTRACT_CHECK'],
                                       variables.abstract_create.format(analysis_MonthYear=analysis_MonthYear, table_data_str=table_data_str, legend=legend),
                                       variables.abstract_check,
                                       4096)

    return analysis_content