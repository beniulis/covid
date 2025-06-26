import pandas as pd

def load_covid_data(path='data/owid-covid-data.csv'):
    df = pd.read_csv(path, parse_dates=['date'])
    return df

def preview_data(df):
    print(df.head())