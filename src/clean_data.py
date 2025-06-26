def filter_country(df, country='United States'):
    columns = ['location', 'date', 'new_cases', 'new_deaths']
    df = df[columns]
    return df[df['location'] == country].reset_index(drop=True)