
import os
import datetime
import variables
import shutil
import markdown
import re
import msal
import requests
import logging
from onedrivedownloader import download
import pandas as pd

from reporttext import openai_mail

def download_onedrive_file(url:str, filename: str):
    """
    Download file from OneDrive

    Args:
        url (str): the OneDrive URL to download the file
        filename (str): the file name to save
    
    Returns:
        None
    """
    max_attempts = 10
    attempts = 0
    content = None

    while attempts < max_attempts:
        try:
            content = download(url, filename, unzip=False)
            if content == "subscriber.xlsx":
                logging.info('The subscriber list downloaded successfully.')
                return True
            else:
                logging.error('Failed to download the subscriber list.')
                logging.error(content)
                return False
        except Exception as e:
            logging.error(f'Failed to download the subscriber list. Error: {e}')
        attempts += 1

    logging.error(f'Failed to download the subscriber list after {max_attempts} attempts.')
    return False


def get_subscriber_list(url:str, file_name = "subscriber.xlsx"):
    """
    Get subscriber list from Onedrive share link

    
    Args:
        url (str): the OneDrive URL to download the file
        filename (str): the file name to save
    
    Returns:
        df: a dataframe contains subscriber list

    """
    if os.path.exists(file_name):
        os.remove(file_name)
    result = download_onedrive_file(url, file_name)

    if result:
        df = pd.read_excel(file_name, sheet_name='Form1')
        df['time'] = df['Completion time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df = df.sort_values('time', ascending=False).drop_duplicates('email_address').sort_index()
        df = df[df['Subscribe'] == 'Subscribe']
        # remove the file
        os.remove(file_name)
        return df
    else:
        return None

def acquire_token(tenant_id, client_id, client_secret):
    """
    Get token from Microsoft Graph

    Args:
        tenant_id: the tenant id of the Azure AD
        client_id: the client id of the Azure AD
        client_secret: the client secret of the Azure AD

    return:
        token
    
    """
    authority_url = f'https://login.microsoftonline.com/{tenant_id}'
    app = msal.ConfidentialClientApplication(
        authority=authority_url,
        client_id=client_id,
        client_credential=client_secret
    )
    token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

    return token

def send_email_graph(access_token, user_id, recipient_email, subject, body):
    """
    Send email using Microsoft Graph API

    Args:
        access_token: the access token to authenticate
        user_id: the user id
        recipient_email: the recipient email
        subject: the email subject
        body: the email body

    return:
        response
    
    """
    endpoint = f'https://graph.microsoft.com/v1.0/users/{user_id}/sendMail'
    email_msg = {
        'Message': {
            'Subject': subject,
            'Body': {'ContentType': 'HTML', 'Content': body},
            'ToRecipients': [{'EmailAddress': {'Address': recipient_email}}]
        },
        'SaveToSentItems': 'true'
    }
    headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
    response = requests.post(endpoint, headers=headers, json=email_msg)
    
    return response

def get_mail_content(test_info, folder_path_mail):
    """
    Get mail content from file

    Args:
        test_info (str): the test info
        folder_path_mail (str): the folder path to mail content
    
    Returns:
        body (str): the mail content in html format
    """
    # read and prepare email content
    with open(os.path.join(folder_path_mail, 'latest_main.md'), 'r') as file:
        body_main = markdown.markdown(file.read())
    with open(os.path.join(folder_path_mail, 'latest_table.md'), 'r') as file:
        body_table = markdown.markdown(file.read(), extensions=['markdown.extensions.tables'])
    
    email_info = markdown.markdown(re.sub(r'(https?://\S+)', r'<a href="\1">\1</a>', variables.email_info))
    if test_info == "True":
        body_main = "<h1>Project still in test mode, please ignore this email.</h1>" + body_main
    body = body_main + email_info + "<h3>Appendix: Notifiable Infectious Diseases Reports: Reported Cases and Deaths of National Notifiable Infectious Diseases</h3>" + body_table
    
    return body

def send_email_to_subscriber(test_info, mail_subject, folder_path_mail):
    """
    Send email to all subscribers

    Args:
        test_info (str): weather the project is in test mode
        folder_path_mail (str): the folder path to mail content

    Returns:
        None
    """
    # load microsoft graph api credentials
    tenant_id = os.environ['mail_tenant_id']
    user_id = os.environ['mail_user_id']
    client_id = os.environ['mail_client_id']
    client_secret = os.environ['mail_client_secret']
    
    # get token from Microsoft Graph
    token = acquire_token(tenant_id, client_id, client_secret)
    if "access_token" in token:
        logging.info("Microsoft Graph API token acquired successfully.")
    else:
        logging.error("Failed to acquire Microsoft Graph API token.")
        return None
    
    # get subscriber list
    df = get_subscriber_list(os.environ['onedrive_url'])
    recipient_emails = df['email_address'].tolist()
    recipient_names = df['Name'].tolist()
    recipient_ids = df['ID'].tolist()

    # get mail content
    body = get_mail_content(test_info, folder_path_mail)

    # send email to all subscribers using Graph API
    for recipient_email, recipient_name, recipient_id in zip(recipient_emails, recipient_names, recipient_ids):
        # replace the recipient name
        send_body = body.replace("[Recipient]", recipient_name)
        send_result = send_email_graph(token["access_token"], user_id, recipient_email, mail_subject, send_body)
        if send_result.status_code == 202:
            logging.info(f"Email sent to {recipient_id} successfully.")
        else:
            logging.error(f"Failed to send email to {recipient_id}.")
            logging.error(send_result.text)

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