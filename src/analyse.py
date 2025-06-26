def peak_cases(df):
    peak = df.loc[df['new_cases'].idxmax()]
    return peak['date'], peak['new_cases']

def add_rolling_average(df, window=7):
    df['rolling_avg'] = df['new_cases'].rolling(window).mean()
    return df