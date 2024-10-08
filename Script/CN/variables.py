# email information
email_info = "\n\n\n\nFurther support: lkg1116@outlook.com" + "\n\nDashboard Link: https://globalinfectiousdisease.com/" + "\n\nData Source: https://github.com/xmusphlkg/globalID/tree/main/Data" + "\n\nUnsubscribe: https://forms.office.com/r/EJUEfKkttK"
email_head = "I hope this email finds you well. China CDC has published the new data on the cases and deaths of notifiable infectious diseases in Chinese mainland in {analysis_YearMonth}."
email_end = "The notion generated automatically, and assistant by AI. Please check the data and description carefully."
email_sign = "Best regards,\nNIDS"

# links to application
links_app = "https://globalinfectiousdisease.com/"

# links to website
links_web = "https://globalinfectiousdisease.com/"

# project description
cover_project = "NIDS: Notifiable Infectious Diseases Surveillance Project"
cover_title_1 = "Notifiable Infectious Diseases"
cover_title_2 = "Surveillance Report"
cover_info_1 = "Automatically Generate by Python and generative AI"
cover_info_2 = "Power by: Github Action"
cover_info_3 = "Design by: Kangguo Li"
cover_info_4 = "Generated Date: {date_now}"
cover_info_5 = "Cite Us: NIDs: Notifiable Infectious Diseases Surveillance Project. <u><a href='https://globalinfectiousdisease.com/'>Github</a></u>"

# default cover
cover_image = "https://source.unsplash.com/collection/94734566/1024x1792"

# alert information
alert_title = "Chinese Notifiable Infectious Diseases Surveillance Report<br/><br/>IMPORTANT"
alert_content = "The text in report is generated automatically by generative AI."

# page words limit
introduction_words = 100
highlights_words = 110
caseanalysis_words = 230
deathanalysis_words = 230

# analysis date range
analysis_years = 10

# Prompt
## abstract
abstract_create = """Craft an epidemiological report analyzing the prevalence and impact of various diseases in Chinese mainland for the specified month and year, {analysis_MonthYear}.
The report should not only focus on diseases with a high incidence but also those that are of public concern, siginificant increase in cases or deaths, or have a high mortality rate.
The report should be between 1000 and 1200 words, structured as follows:
## Overview
2 paragraphs to analysis cases and deaths, respectively.
## Concerns
2 paragraphs to analysis high incidence disease and public concern, respectively.
## Recommendations
2-3 paragraphs to provided the recommendations for the public.
Use the provided data (Cases/Deaths) to support the analysis.
{table_data_str}.
{legend}"""
abstract_check = """Analyze the following text and tell me if it is indeed the abstract of report and includes the sub-sections "## Overview", "## Concerns" and "## Recommendations" respond with 'Yes'.
If these conditions are not met, respond with 'No'.
{content_raw}"""
# news
news_create_nation = """Conduct a comprehensive yet concise search and summarize infectious disease events in Chinese mainland since {analysis_MonthYear}.
The summary should be structured as follows:
## Summary
(Provide an overall summary of the infectious disease events)
### Outbreaks of Known Diseases
(Detail the outbreaks of known diseases during this period)
### Emergence of Novel Pathogens
(Discuss any new pathogens that have emerged)
"""
news_clean_nation = """Clean the following text and generate a new summary using below format (words limited 800 - 1000):
## Summary
(Provide an overall summary of the infectious disease events)
### Outbreaks of Known Diseases
(Detail the outbreaks of known diseases during this period)
### Emergence of Novel Pathogens
(Discuss any new pathogens that have emerged)
This is content you need to clean:
{content_raw}"""
news_check_nation = """Analyze the following text and tell me if it is a summary of infectious diseases report and includes the sub-sections "## Summary", "## Concerns" and "## Recommendations" respond with 'Yes'.
If these conditions are not met, respond with 'No'.
{content_clean}"""
news_create_global = """Conduct a comprehensive yet concise search and summarize infectious disease events globally since {analysis_MonthYear}. 
The summary should be structured as follows:
## Summary
(Provide an overall summary of the infectious disease events)
### Outbreaks of Known Diseases
(Detail the outbreaks of known diseases during this period)
### Emergence of Novel Pathogens
(Discuss any new pathogens that have emerged)
"""
news_clean_global = """Clean the following text and generate a new summary using below format (words limited 800 - 1000):
## Summary
(Provide an overall summary of the infectious disease events)
### Outbreaks of Known Diseases
(Detail the outbreaks of known diseases during this period)
### Emergence of Novel Pathogens
(Discuss any new pathogens that have emerged)
This is content you need to clean:
{content_raw}"""
news_check_global = """Analyze the following text and tell me if it is a summary of infectious diseases report and includes the sub-sections "## Summary", "## Concerns" and "## Recommendations" respond with 'Yes'.
If these conditions are not met, respond with 'No'.
{content_clean}"""

## introduction
introduction_create = "Give a brief introduction to {disease_name}, not give any comment (words limit 90 - 100 words)."
introduction_check = "Analyze the following text and tell me if it is the Introduction section to {disease_name} report. If it is, please answer me Yes. If not, please answer me No."
## Highlights
highlights_create = """Analyze the provided data for {disease_name} in Chinese mainland
and provide a brief summary of key epidemiological trends and the current disease situation as of {report_date}.
The summary should be formatted as a list of highlights (3-4 elements), each one followed by a line break <br/>.
The word count should be between 100 and 110 words. Here is the data for {disease_name} in Chinese mainland:
{table_data_str}"""
highlights_check = "Analyze the following text and tell me if it is the Highlights section to {disease_name} report. If it is, please answer me Yes. If not, please answer me No."
## Analysis
caseanalysis_create = """Provide a deep cases analysis of the reported data for {disease_name} in Chinese mainland, only 2 - 3 paragraphs and not give subject point.
Here is the data for {disease_name} in Chinese mainland:
{table_data_str}"""
caseanalysis_check = """Evaluate the given text and determine whether it corresponds to the cases analysis section of a report related to {disease_name}.
If it is indeed the cases analysis section respond with 'Yes'.
If these conditions are not met, respond with 'No'."""

deathanalysis_create = """Provide a deep deaths analysis of the reported data for {disease_name} in Chinese mainland, only 2 - 3 paragraphs and not give subject point.
Here is the data for {disease_name} in Chinese mainland:
{table_data_str}"""
deathanalysis_check = """Evaluate the given text and determine whether it corresponds to the deaths analysis section of a report related to {disease_name}.
If it is indeed the deaths analysis section respond with 'Yes'.
If these conditions are not met, respond with 'No'."""

## mail
mail_create = """Analyze the provided monthly data on cases and deaths related to various diseases in mainland China for the month of {analysis_YearMonth}.
Create a summary of key points focusing on infectious diseases, highlighting those that require particular attention. 
Use the provided data (Cases/Deaths) to substantiate the analysis. 
Here is the data: 

{table_data_str}, 

and the legend: 
{table_legend}."""
mail_check = """Analyze the following text and tell me if it is a short list of important points of infectious diseases. If it is, please answer me Yes. If not, please answer me No.
{content_raw}"""
## cover image
key_create = """Analyze below content, and give a prompt to create a abstract cover image of this report.
Keep the cover as simple as possible. Don't touch on any text or statistical charts.
The background color should be darkblue. The image theme is technology.
{mail_content}"""
key_check = """Analyze the following text and tell me if it is a Prompt. If it is, please answer me Yes. If not, please answer me No.
{content_raw}"""
