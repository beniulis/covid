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
    
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': c, 'value': c} for c in sorted(df['country'].unique())],
        value='United Kingdom'
    ),
    
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

@app.callback(
    [Output('cases-plot', 'figure'),
     Output('deaths-plot', 'figure')],
    [Input('country-dropdown', 'value'),
     Input('date-slider', 'value'),
     Input('lock-deaths', 'value')],
    State('deaths-plot', 'figure')
)
def update_plots(selected_country, date_range_idx, lock_deaths, previous_deaths_fig):
    # Convert slider indices to dates
    start_date = date_options[date_range_idx[0]]
    end_date = date_options[date_range_idx[1]]
    
    # Filter data
    country_df = df[(df['country'] == selected_country) &
                    (df['date'] >= start_date) &
                    (df['date'] <= end_date)]
    
    title = (
            f"COVID-19 Daily New Cases in {selected_country}"
            f"<br>({start_date.strftime('%Y-%m')} to {end_date.strftime('%Y-%m')})"
)

    # --- Case Plot ---
    fig_cases = px.line(
        country_df, x='date', y=['new_cases', 'rolling_avg_cases'],
        labels={'value': 'Cases', 'date': 'Date', 'variable': 'Metric'},
        title=title
    )
    fig_cases.update_layout(legend_title_text='Metric', template='plotly_white')

    # --- Death Plot ---
    if 'lock' in lock_deaths and previous_deaths_fig:
        fig_deaths = previous_deaths_fig  # Keep previous
    else:
        title = (
            f"COVID-19 Daily New Deaths in {selected_country}"
            f"<br>({start_date.strftime('%Y-%m')} to {end_date.strftime('%Y-%m')})"
        )
        fig_deaths = px.line(
            country_df, x='date', y=['new_deaths', 'rolling_avg_deaths'],
            labels={'value': 'Deaths', 'date': 'Date', 'variable': 'Metric'},
            title=title
        )
        fig_deaths.update_layout(legend_title_text='Metric', template='plotly_white')

    return fig_cases, fig_deaths

# Run server
if __name__ == '__main__':
    app.run_server(debug=True)