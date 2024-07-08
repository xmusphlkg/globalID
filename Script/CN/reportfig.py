
import pandas as pd
import os
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
    data = disease_data.copy()
    data = data[['Date', 'Cases']]

    fig = go.Figure(layout=go.Layout(
        title=go.layout.Title(text=f'{disease}'),
        xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text='Date')),
        yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text='Cases')),
        template='plotly_white'
    ))
    fig.add_trace(go.Scatter(x = disease_data['Date'],
                            y = disease_data['Cases'],
                            mode='lines',
                            name=disease,
                            hovertemplate='Date: %{x}<br>Cases: %{y}'))
    plot_html_1 = fig.to_html(full_html=False, include_plotlyjs=False)

    # Deaths over time
    data = disease_data.copy()
    data = data[['Date', 'Deaths']]
    fig = go.Figure(layout=go.Layout(
        title=go.layout.Title(text=f'{disease}'),
        xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text='Date')),
        yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text='Deaths')),
        template='plotly_white'
    ))
    fig.add_trace(go.Scatter(x = disease_data['Date'],
                            y = disease_data['Deaths'],
                            mode='lines',
                            name=disease,
                            hovertemplate='Date: %{x}<br>Deaths: %{y}'))
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
    data = data.pivot(index='Month', columns='Year', values='Cases')

    fig = go.Figure(layout=go.Layout(
        title=go.layout.Title(text=f'{disease}'),
        xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text='Year')),
        yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text='Month')),
        template='plotly_white'
    ))
    fig.add_trace(go.Heatmap(z=data.values,
                             x=data.columns,
                             y=data.index,
                             colorscale='Viridis'))
    plot_html_3 = fig.to_html(full_html=False, include_plotlyjs=False)

    # Deaths over time
    data = disease_data.copy()
    data = data[['Year', 'Month', 'Deaths']]
    data = data.pivot(index='Month', columns='Year', values='Deaths')

    fig = go.Figure(layout=go.Layout(
        title=go.layout.Title(text=f'{disease}'),
        xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text='Year')),
        yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text='Month')),
        template='plotly_white'
    ))
    fig.add_trace(go.Heatmap(z=data.values,
                             x=data.columns,
                             y=data.index,
                             colorscale='Viridis'))
    plot_html_4 = fig.to_html(full_html=False, include_plotlyjs=False)

    return plot_html_3, plot_html_4