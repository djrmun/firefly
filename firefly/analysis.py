import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

def load_data_from_db(db_path: str) -> pd.DataFrame:
    """
    Loads performance metrics from the SQLite database into a pandas DataFrame.
    """
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at '{db_path}'")
        return pd.DataFrame()

    try:
        with sqlite3.connect(db_path) as conn:
            query = "SELECT timestamp, url, http_code, time_namelookup, time_connect, time_appconnect, time_pretransfer, time_starttransfer, time_total, hostname, network_interface FROM metrics WHERE error IS NULL"
            df = pd.read_sql_query(query, conn)

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        # Create a combined environment column for easier grouping
        df['environment'] = df['hostname'] + ' (' + df['network_interface'] + ')'
        return df

    except Exception as e:
        print(f"An error occurred while reading the database: {e}")
        return pd.DataFrame()


def calculate_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates summary statistics for the metrics, grouped by environment and URL.
    """
    if df.empty:
        return pd.DataFrame()

    metrics_to_analyze = [
        'time_total',
        'time_namelookup',
        'time_connect',
        'time_starttransfer'
    ]

    aggregations = ['mean', 'min', 'max', lambda x: x.quantile(0.95)]

    # Group by the new environment column and URL
    stats = df.groupby(['environment', 'url'])[metrics_to_analyze].agg(aggregations).rename(columns={'<lambda_0>': '95th_percentile'})

    return stats


def plot_metrics_over_time(df: pd.DataFrame, output_path: str):
    """
    Generates a plot of 'time_total' over time, with separate lines for each
    environment-URL combination.
    """
    if df.empty:
        print("Cannot generate plot: DataFrame is empty.")
        return

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(15, 8))

    # Create a unique identifier for each line to plot
    df['plot_label'] = df['url'] + ' @ ' + df['environment']

    for label in df['plot_label'].unique():
        subset = df[df['plot_label'] == label]
        ax.plot(subset['timestamp'], subset['time_total'], marker='o', linestyle='-', label=label)

    ax.set_title('Total Request Time Over Time by Environment')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Total Time (seconds)')
    ax.legend(loc='best', fontsize='small')
    plt.xticks(rotation=30)
    plt.tight_layout()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")


def generate_report(db_path: str, output_dir: str = "reports"):
    """
    Loads data, calculates statistics, and generates a plot.
    """
    df = load_data_from_db(db_path)
    if df.empty:
        print("No data available to generate a report.")
        return

    stats = calculate_statistics(df)
    print("\n--- Performance Statistics (grouped by Environment and URL) ---")
    # Use to_string() to ensure the whole table is printed
    print(stats.to_string())
    print("-------------------------------------------------------------")

    plot_path = os.path.join(output_dir, "performance_by_environment.png")
    plot_metrics_over_time(df, plot_path)


if __name__ == '__main__':
    DB_FILE = "firefly_metrics.db"
    if not os.path.exists(DB_FILE):
        print(f"Database file '{DB_FILE}' not found.")
        print("Please run the monitor first to generate some data.")
    else:
        # To test, we need to ensure the DB has the new columns.
        # It's safest to delete the old DB and regenerate it.
        print("Generating report...")
        generate_report(DB_FILE)
