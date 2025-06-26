import pandas as pd

def load_and_prepare_data(csv_path='data/owid-covid-data.csv'):
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    df = df[['date', 'location', 'new_cases', 'new_deaths']].copy()
    df.rename(columns={'location': 'country'}, inplace=True)

    # Rolling averages
    df['rolling_avg_cases'] = df.groupby('country')['new_cases'].transform(lambda x: x.rolling(7).mean())
    df['rolling_avg_deaths'] = df.groupby('country')['new_deaths'].transform(lambda x: x.rolling(7).mean())
    
    return df