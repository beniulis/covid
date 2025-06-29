import streamlit as st
import plotly.graph_objects as go
import plotly.colors as pc
import pandas as pd
from covid_utils import load_and_prepare_data
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="COVID-19 Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- Load and preprocess data ---
@st.cache_data
def load_data():
    df = load_and_prepare_data()
    df['date'] = pd.to_datetime(df['date'])
    
    # Clean and aggregate data (for weekly data)
    def clean_weekly_data(df_sub, country=None):
        # Sort by date and remove duplicates by keeping the last entry for each date
        df_sub = df_sub.sort_values('date').drop_duplicates(subset=['date'], keep='last')
        
        # Remove any rows where both new_cases and new_deaths are 0 (likely padding artifacts)
        df_sub = df_sub[(df_sub['new_cases'] > 0) | (df_sub['new_deaths'] > 0)]
        
        df_sub['country'] = country
        return df_sub.reset_index(drop=True)

    # Apply cleaning to each country group
    cleaned_dfs = []
    for country in df['country'].unique():
        country_df = df[df['country'] == country]
        cleaned_df = clean_weekly_data(country_df[['date', 'new_cases', 'new_deaths']], country=country)
        cleaned_dfs.append(cleaned_df)

    df = pd.concat(cleaned_dfs, ignore_index=True)
    return df

# Load data
df = load_data()

# --- App Title ---
st.title("📊 COVID-19 Weekly Cases and Deaths by Country")

# --- Sidebar Controls ---
st.sidebar.header("Dashboard Controls")

# Country selection
countries = sorted(df['country'].unique())

cases_countries = st.sidebar.multiselect(
    "Select Countries for Cases Comparison:",
    countries,
    default=['United Kingdom']
)

deaths_countries = st.sidebar.multiselect(
    "Select Countries for Deaths Comparison:",
    countries,
    default=['United Kingdom']
)

# Date range selection
min_date = df['date'].min().date()
max_date = df['date'].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Handle single date selection
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

# Convert to datetime for filtering
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# --- Filter Data ---
filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy()

# --- Create Plots ---
color_sequence = pc.qualitative.Set1 + pc.qualitative.Set2 + pc.qualitative.Set3

# Cases Plot
def create_cases_plot():
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
                connectgaps=False
            ))

    fig_cases.update_layout(
        title=f"Weekly New COVID-19 Cases<br>({start_date.strftime('%Y-%m')} to {end_date.strftime('%Y-%m')})",
        template='plotly_white',
        xaxis=dict(title='Date', type='date'),
        yaxis=dict(title='New Cases'),
        legend_title="Country",
        hovermode='x unified',
        height=500
    )
    
    return fig_cases

# Deaths Plot  
def create_deaths_plot():
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
        hovermode='x unified',
        height=500
    )
    
    return fig_deaths

# --- Display Plots ---
col1, col2 = st.columns(2)

with col1:
    if cases_countries:
        st.plotly_chart(create_cases_plot(), use_container_width=True)
    else:
        st.info("Please select at least one country for cases comparison.")

with col2:
    if deaths_countries:
        st.plotly_chart(create_deaths_plot(), use_container_width=True)
    else:
        st.info("Please select at least one country for deaths comparison.")

# --- Data Summary ---
if st.sidebar.checkbox("Show Data Summary"):
    st.subheader("Data Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Countries", len(df['country'].unique()))
    
    with col2:
        st.metric("Date Range", f"{min_date} to {max_date}")
    
    with col3:
        st.metric("Total Data Points", len(filtered_df))
    
    # Show sample data
    if st.checkbox("Show Raw Data Sample"):
        st.dataframe(filtered_df.head(20))

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.markdown("*COVID-19 Dashboard built with Streamlit*")