import matplotlib.pyplot as plt

def plot_cases(df, output_path='results/plots/cases_plot.png'):
    plt.figure(figsize=(12,6))
    plt.plot(df['date'].to_numpy(), df['new_cases'].to_numpy(), label='Daily New Cases')
    plt.plot(df['date'].to_numpy(), df['rolling_avg'].to_numpy(), label='7-Day Avg', linewidth=2)
    plt.xlabel('Date')
    plt.ylabel('Cases')
    plt.title('COVID-19 Daily Cases')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved plot to {output_path}")