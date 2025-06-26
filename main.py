import os
from src import load_data, clean_data, analyse, visualise

def main():
    os.makedirs('results/plots', exist_ok=True)

    df = load_data.load_covid_data()
    df = clean_data.filter_country(df, country='United States')
    date, cases = analyse.peak_cases(df)
    print(f"Peak new cases: {int(cases)} on {date.date()}")
    df = analyse.add_rolling_average(df)
    visualise.plot_cases(df)

if __name__ == '__main__':
    main()