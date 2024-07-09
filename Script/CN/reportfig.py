
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import variables

def prepare_disease_data(df, disease):
    """
    Prepare disease data for plotting.

    Parameters:
    - df: A pandas DataFrame with 'Diseases', 'Date', 'Cases', and 'Deaths' columns.
    - disease: The name of the disease to filter the DataFrame on.

    Returns:
    - A pandas DataFrame processed to include only the relevant disease data, with missing dates filled in.
    """
    # Filter data for the specified disease
    disease_data = df[df['Diseases'] == disease].copy()
    # formate date
    disease_data['Date'] = pd.to_datetime(disease_data['Date']).dt.date
    disease_data = disease_data.sort_values(by='Date', ascending=True)
    # drop unnecessary columns
    disease_data = disease_data[['YearMonthDay', 'Cases', 'Deaths']]
    # complete missing dates
    dates_unrecognized = pd.date_range(disease_data['YearMonthDay'].min(), disease_data['YearMonthDay'].max(), freq='MS').strftime('%Y/%m/%d')
    dates_unrecognized = list(set(dates_unrecognized) - set(disease_data['YearMonthDay']))
    missing_data = pd.DataFrame({'YearMonthDay': dates_unrecognized, 'Cases': None, 'Deaths': None})
    disease_data = pd.concat([disease_data, missing_data])
    # sort by date
    disease_data = disease_data.sort_values(by='YearMonthDay', ascending=True)
    disease_data = disease_data.reset_index()
    disease_data = disease_data.drop(['index'], axis=1)
    # formate date
    disease_data['Date'] = pd.to_datetime(disease_data['YearMonthDay'])
    disease_data['YearMonth'] = disease_data['Date'].dt.strftime('%Y %B')

    # table
    disease_data['Year'] = disease_data['Date'].dt.year
    disease_data['Month'] = disease_data['Date'].dt.month
    disease_data = disease_data.drop_duplicates(subset=['Year', 'Month'])
    
    return disease_data

def calculate_dtick(y_values):
    """
    Calculate an appropriate Y-axis tick interval based on the maximum Y value.
    
    Args:
        y_values (list or array): Array or list of Y values from the data.
    
    Returns:
        int: Suggested tick interval for Y axis.
    """

    y_max = np.max(y_values)
    
    dtick = int(np.ceil(y_max / 5))
    
    dtick = max(1, dtick)

    range = dtick * 5
    
    return dtick, range

def plot_disease_data(disease_data, disease):
    """
    Plot disease cases and deaths over time and return html plotly figure.

    Args:
        disease_data (dataframe): the disease data
        disease (str): the disease name
    Returns:
        str: the plotly figure in html format
    """
    # Cases over time
    dtick, range = calculate_dtick(disease_data['Cases'])

    fig = go.Figure(layout=go.Layout(
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(text='Date')
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(text='Cases'),
            rangemode='tozero',  # start from zero
            tickformat=',d',  # integer format
            dtick=dtick,
            range=[0, range]
        ),
        template='ggplot2',
        margin=dict(l=0, r=50, t=0, b=100),
        autosize=True
    ))
    fig.add_trace(go.Scatter(
        x=disease_data['Date'],
        y=disease_data['Cases'],
        mode='lines',
        name=disease,
        hovertemplate='Date: %{x}<br>Cases: %{y:,}',
        line=dict(color='rgb(23,40,105)')
    ))
    plot_html_1 = fig.to_html(full_html=False, include_plotlyjs=False)

    # Deaths over time
    dtick, range = calculate_dtick(disease_data['Deaths'])

    fig = go.Figure(layout=go.Layout(
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(text='Date')
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(text='Deaths'),
            rangemode='tozero',  # start from zero
            tickformat=',d',  # integer format
            dtick=dtick,
            range=[0, range]
        ),
        template='ggplot2',
        margin=dict(l=0, r=50, t=0, b=100),
        autosize=True
    ))
    fig.add_trace(go.Scatter(
        x=disease_data['Date'],
        y=disease_data['Deaths'],
        mode='lines',
        name=disease,
        hovertemplate='Date: %{x}<br>Deaths: %{y:,}',
        line=dict(color='rgb(98,129,11)')
    ))
    plot_html_2 = fig.to_html(full_html=False, include_plotlyjs=False)

    return plot_html_1, plot_html_2


def plot_disease_heatmap(disease_data, disease):
    """
    Plot heatmap for cases and deaths over time and return html plotly figure.

    Args:
        disease_data (dataframe): the disease data
        disease (str): the disease name

    Returns:
        str: the plotly figure in html format
    """

    # Cases over time
    data = disease_data.copy()
    data = data[['Year', 'Month', 'Cases']]
    data = data.pivot(index='Year', columns='Month', values='Cases')

    fig = go.Figure(layout=go.Layout(
        xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text='Month'), tickmode='linear'),
        yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text='Year'), tickmode='linear'),
        template='ggplot2',
        margin=dict(l=0, r=50, t=0, b=100)
    ))
    fig.add_trace(go.Heatmap(z=data.values,
                             y=data.index,
                             x=data.columns,
                             name=disease,
                             colorscale=[[0, 'rgb(175,223,239)'], [1, 'rgb(23,40,105)']],
                             hovertemplate='Month: %{x}<br>Year: %{y}<br>Cases: %{z:,}'))
    plot_html_3 = fig.to_html(full_html=False, include_plotlyjs=False)

    # Deaths over time
    data = disease_data.copy()
    data = data[['Year', 'Month', 'Deaths']]
    data = data.pivot(index='Year', columns='Month', values='Deaths')

    fig = go.Figure(layout=go.Layout(
        xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text='Month'), tickmode='linear'),
        yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text='Year'), tickmode='linear'),
        template='ggplot2',
        margin=dict(l=0, r=50, t=0, b=100)
    ))
    fig.add_trace(go.Heatmap(z=data.values,
                             y=data.index,
                             x=data.columns,
                             name=disease,
                             colorscale=[[0, 'rgb(236,234,8)'], [1, 'rgb(98,129,11)']],
                             hovertemplate='Month: %{x}<br>Year: %{y}<br>Deaths: %{z:,}'))
    plot_html_4 = fig.to_html(full_html=False, include_plotlyjs=False)

    return plot_html_3, plot_html_4