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

monthly_marks = {}
for i, date in enumerate(df_dates):
    if pd.to_datetime(date).day == 1 and i % 2 == 0:  # every 2nd month
        monthly_marks[i] = {'label': f"{date.strftime('%b')}<br>{date.strftime('%Y')}"}

year_marks = {}
for i, date in enumerate(df_dates):
    if date.month == 1:  # January only for marks
        year_marks[i] = str(date.year)

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
        max=len(df_dates) - 1,
        value=[0, len(df_dates) - 1],
        marks=year_marks,
        step=1,  # step by 1 month
        tooltip={"placement": "bottom", "always_visible": False}
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
    df_dates = df['date'].sort_values().unique()
    start_date = df_dates[date_range_idx[0]]
    end_date = df_dates[date_range_idx[1]]
    
    # Filter data
    country_df = df[(df['country'] == selected_country) &
                    (df['date'] >= start_date) &
                    (df['date'] <= end_date)]

    # --- Case Plot ---
    fig_cases = px.line(
        country_df, x='date', y=['new_cases', 'rolling_avg_cases'],
        labels={'value': 'Cases', 'date': 'Date', 'variable': 'Metric'},
        title=f"COVID-19 Daily New Cases in {selected_country}"
    )
    fig_cases.update_layout(legend_title_text='Metric', template='plotly_white')

    # --- Death Plot ---
    if 'lock' in lock_deaths and previous_deaths_fig:
        fig_deaths = previous_deaths_fig  # Keep previous
    else:
        fig_deaths = px.line(
            country_df, x='date', y=['new_deaths', 'rolling_avg_deaths'],
            labels={'value': 'Deaths', 'date': 'Date', 'variable': 'Metric'},
            title=f"COVID-19 Daily New Deaths in {selected_country}"
        )
        fig_deaths.update_layout(legend_title_text='Metric', template='plotly_white')

    return fig_cases, fig_deaths

# Run server
if __name__ == '__main__':
    app.run_server(debug=True)