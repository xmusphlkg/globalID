
import os
import datetime
from reporttext import openai_mail
import variables
import shutil

def generate_mail(table_data_str, table_legend, analysis_YearMonth):
    """
    Generate mail content and save to file

    Args:
        table_data (dataframe): the table data
        table_legend (str): the table legend
        analysis_YearMonth (str): the analysis year and month
        mail_path (str): the mail path

    Returns:
        mail_content
    """
    
    # create mail main
    mail_main = openai_mail(os.environ['MAIL_MAIN_CREATE'],
                            os.environ['MAIL_MAIN_CHECK'],
                            variables.mail_create.format(table_data_str=table_data_str, table_legend=table_legend, analysis_YearMonth=analysis_YearMonth),
                            variables.mail_check)
    mail_head = "Dear [Recipient],"
    mail_info = variables.email_head.format(analysis_YearMonth=analysis_YearMonth)
    mail_end = variables.email_end
    mail_signature = variables.email_sign
    mail_time = datetime.datetime.now().strftime("%Y-%m-%d")
    mail_content = mail_head + "\n\n" + mail_info + "\n\n" + mail_main + "\n\n" + mail_end + "\n\n" + mail_signature + "\n\n" + mail_time + "\n\n"

    mail_content = generate_mail(mail_main, analysis_YearMonth)

    return mail_content


def create_mail_table(table_data, analysis_YearMonth, mail_path):
    """
    Generate mail content and save to file

    Args:
        table_data_str (str): the table data string
        table_legend (str): the table legend
        analysis_YearMonth (str): the analysis year and month
        mail_path (str): the mail path

    Returns:
        None
    """
    # create mail table
    with open(os.path.join(mail_path, f'{analysis_YearMonth}_table.md'), 'w') as f:
        f.write(table_data)
    shutil.copyfile(os.path.join(mail_path, f'{analysis_YearMonth}_table.md'), os.path.join(mail_path, 'latest_table.md'))