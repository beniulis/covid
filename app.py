import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.colors as pc
import pandas as pd
from covid_utils import load_and_prepare_data

# --- Load and preprocess data ---
df = load_and_prepare_data()
df['date'] = pd.to_datetime(df['date'])

# --- Clean and aggregate data (for weekly data) ---
def clean_weekly_data(df_sub, country=None):
    # Sort by date and remove duplicates by keeping the last entry for each date
    df_sub = df_sub.sort_values('date').drop_duplicates(subset=['date'], keep='last')
    
    # Remove any rows where both new_cases and new_deaths are 0 (likely padding artifacts)
    df_sub = df_sub[(df_sub['new_cases'] > 0) | (df_sub['new_deaths'] > 0)]
    
    df_sub['country'] = country
    return df_sub.reset_index(drop=True)

# Apply cleaning to each country group
df = df.groupby('country', group_keys=False).apply(
    lambda g: clean_weekly_data(g[['date', 'new_cases', 'new_deaths']], country=g.name), include_groups=False
)

# --- Generate date list for slider ---
df_dates = df['date'].sort_values().unique()
unique_dates = pd.Series(df_dates).dt.to_period('M').drop_duplicates().dt.to_timestamp()
date_options = list(unique_dates)
slider_marks = {i: date.strftime('%Y') for i, date in enumerate(date_options) if date.month == 1}

# --- Dash App Setup ---
app = dash.Dash(__name__)
app.title = "COVID-19 Dashboard"

app.layout = html.Div([
    html.H1("COVID-19 Weekly Cases and Deaths by Country"),

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

    # dcc.Checklist(
    #     id='lock-deaths',
    #     options=[{'label': 'Lock deaths plot', 'value': 'lock'}],
    #     value=[],
    #     style={'margin': '20px 0'}
    # ),

    html.Div([
        dcc.Graph(id='cases-plot', style={'display': 'inline-block', 'width': '49%'}),
        dcc.Graph(id='deaths-plot', style={'display': 'inline-block', 'width': '49%'})
    ])
])

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

    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy()
    color_sequence = pc.qualitative.Set1 + pc.qualitative.Set2 + pc.qualitative.Set3

    # --- Case Plot ---
    fig_cases = go.Figure()
    for i, country in enumerate(cases_countries):
        country_df = filtered_df[filtered_df['country'] == country].sort_values('date')
        if not country_df.empty:
            fig_cases.add_trace(go.Scatter(
                x=country_df['date'],
                y=country_df['new_cases'],
                mode='lines+markers',
                name=country,
                line=dict(color=color_sequence[i % len(color_sequence)], width=3, shape='spline'),
                marker=dict(size=4),
                connectgaps=False  # Don't connect gaps, let spline handle smoothing
            ))

    fig_cases.update_layout(
        title=f"Weekly New COVID-19 Cases<br>({start_date.strftime('%Y-%m')} to {end_date.strftime('%Y-%m')})",
        template='plotly_white',
        xaxis=dict(title='Date', type='date'),
        yaxis=dict(title='New Cases'),
        legend_title="Country",
        hovermode='x unified'
    )

    # --- Death Plot ---
    fig_deaths = go.Figure()
    for i, country in enumerate(deaths_countries):
        country_df = filtered_df[filtered_df['country'] == country].sort_values('date')
        if not country_df.empty:
            fig_deaths.add_trace(go.Scatter(
                x=country_df['date'],
                y=country_df['new_deaths'],
                mode='lines+markers',
                name=country,
                line=dict(color=color_sequence[i % len(color_sequence)], width=3, shape='spline'),
                marker=dict(size=4),
                connectgaps=False
            ))

    fig_deaths.update_layout(
        title=f"Weekly New COVID-19 Deaths<br>({start_date.strftime('%Y-%m')} to {end_date.strftime('%Y-%m')})",
        template='plotly_white',
        xaxis=dict(title='Date', type='date'),
        yaxis=dict(title='New Deaths'),
        legend_title="Country",
        hovermode='x unified'
    )

    return fig_cases, fig_deaths

# Run server
if __name__ == '__main__':
    app.run_server(debug=True)