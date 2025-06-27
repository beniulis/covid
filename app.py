import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
from covid_utils import load_and_prepare_data

# Load data
df = load_and_prepare_data()

# --- Generate date list for slider ---
df_dates = df['date'].sort_values().unique()

# In your Dash setup
unique_dates = df['date'].dt.to_period('M').drop_duplicates().dt.to_timestamp()
date_options = list(unique_dates)

# Use index for slider
slider_marks = {i: date.strftime('%Y') for i, date in enumerate(date_options) if date.month == 1}  # Show only Januarys

app = dash.Dash(__name__)
app.title = "COVID-19 Dashboard"

app.layout = html.Div([
    html.H1("COVID-19 Daily Cases and Deaths by Country"),
    
    html.Div([
        html.Div([
            html.Label("Compare Countries by Cases"),
            dcc.Dropdown(
                id='cases-countries-dropdown',
                options=[{'label': c, 'value': c} for c in sorted(df['country'].unique())],
                value=['United Kingdom'],
                multi=True
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Compare Countries by Deaths"),
            dcc.Dropdown(
                id='deaths-countries-dropdown',
                options=[{'label': c, 'value': c} for c in sorted(df['country'].unique())],
                value=['United Kingdom'],
                multi=True
            )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
    ], style={'margin-bottom': '20px'}),
    
    dcc.RangeSlider(
        id='date-slider',
        min=0,
        max=len(date_options) - 1,
        value=[0, len(date_options) - 1],
        marks=slider_marks,
        step=1,
        allowCross=False,
    ),
    
    dcc.Checklist(
        id='lock-deaths',
        options=[{'label': 'Lock deaths plot', 'value': 'lock'}],
        value=[],
        style={'margin': '20px 0'}
    ),

    html.Div([
        dcc.Graph(id='cases-plot', style={'display': 'inline-block', 'width': '49%'}),
        dcc.Graph(id='deaths-plot', style={'display': 'inline-block', 'width': '49%'})
    ])
])

import plotly.colors as pc

@app.callback(
    [Output('cases-plot', 'figure'),
     Output('deaths-plot', 'figure')],
    [Input('cases-countries-dropdown', 'value'),
     Input('deaths-countries-dropdown', 'value'),
     Input('date-slider', 'value')]
)
def update_plots(cases_countries, deaths_countries, date_range_idx):
    start_date = date_options[date_range_idx[0]]
    end_date = date_options[date_range_idx[1]]

    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    # Define your custom color sequence (choose more if needed)
    color_sequence = pc.qualitative.Set1 + pc.qualitative.Set2 + pc.qualitative.Set3

    # --- Case Plot ---
    cases_df = filtered_df[filtered_df['country'].isin(cases_countries)].copy()
    cases_df['country'] = pd.Categorical(cases_df['country'], categories=cases_countries, ordered=True)
    fig_cases = px.bar(
        cases_df.sort_values(['country', 'date']),
        x='date',
        y='new_cases',
        color='country',
        title=f"Daily New COVID-19 Cases<br>({start_date.strftime('%Y-%m')} to {end_date.strftime('%Y-%m')})",
        color_discrete_sequence=color_sequence[:len(cases_countries)]
    )
    fig_cases.update_layout(template='plotly_white')
    fig_cases.update_traces(opacity=0.7)

    # --- Death Plot ---
    deaths_df = filtered_df[filtered_df['country'].isin(deaths_countries)].copy()
    deaths_df['country'] = pd.Categorical(deaths_df['country'], categories=deaths_countries, ordered=True)
    fig_deaths = px.bar(
        deaths_df.sort_values(['country', 'date']),
        x='date',
        y='new_deaths',
        color='country',
        title=f"Daily New COVID-19 Deaths<br>({start_date.strftime('%Y-%m')} to {end_date.strftime('%Y-%m')})",
        color_discrete_sequence=color_sequence[:len(deaths_countries)]
    )
    fig_deaths.update_layout(template='plotly_white')
    fig_deaths.update_traces(opacity=0.7)

    return fig_cases, fig_deaths

# Run server
if __name__ == '__main__':
    app.run_server(debug=True)