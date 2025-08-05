import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

def load_data_from_db(db_path: str) -> pd.DataFrame:
    """
    Loads performance metrics from the SQLite database into a pandas DataFrame.

    Args:
        db_path: The path to the SQLite database file.

    Returns:
        A pandas DataFrame containing the metrics data. Returns an empty
        DataFrame if the table doesn't exist or there's an error.
    """
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at '{db_path}'")
        return pd.DataFrame()

    try:
        with sqlite3.connect(db_path) as conn:
            # The 'error' column might cause issues if not all rows have it,
            # so we select specific columns.
            query = "SELECT timestamp, url, http_code, time_namelookup, time_connect, time_appconnect, time_pretransfer, time_starttransfer, time_total FROM metrics WHERE error IS NULL"
            df = pd.read_sql_query(query, conn)

        # Convert timestamp to datetime objects
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    except sqlite3.Error as e:
        print(f"SQLite error when reading the database: {e}")
        return pd.DataFrame()
    except Exception as e:
        # This can happen if the table doesn't exist yet
        print(f"An error occurred: {e}")
        return pd.DataFrame()


def calculate_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates summary statistics for the performance metrics, grouped by URL.

    Args:
        df: DataFrame containing the performance metrics.

    Returns:
        A DataFrame with the calculated statistics.
    """
    if df.empty:
        return pd.DataFrame()

    # Define the metrics we want to analyze
    metrics_to_analyze = [
        'time_total',
        'time_namelookup',
        'time_connect',
        'time_starttransfer'
    ]

    # Define the aggregations we want to compute
    aggregations = ['mean', 'min', 'max', lambda x: x.quantile(0.95)]

    # Group by URL and calculate the stats
    stats = df.groupby('url')[metrics_to_analyze].agg(aggregations).rename(columns={'<lambda_0>': '95th_percentile'})

    return stats


def plot_metrics_over_time(df: pd.DataFrame, output_path: str):
    """
    Generates a plot of 'time_total' over time for each URL.

    Args:
        df: DataFrame containing the performance metrics.
        output_path: The path to save the plot image file.
    """
    if df.empty:
        print("Cannot generate plot: DataFrame is empty.")
        return

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(12, 7))

    for url in df['url'].unique():
        subset = df[df['url'] == url]
        ax.plot(subset['timestamp'], subset['time_total'], marker='o', linestyle='-', label=url)

    ax.set_title('Total Request Time Over Time')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Total Time (seconds)')
    ax.legend(loc='best')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")


def generate_report(db_path: str, output_dir: str = "reports"):
    """
    Loads data, calculates statistics, and generates a plot.

    Args:
        db_path: Path to the SQLite database.
        output_dir: Directory to save the report files.
    """
    # Load data
    df = load_data_from_db(db_path)
    if df.empty:
        print("No data available to generate a report.")
        return

    # Calculate and print statistics
    stats = calculate_statistics(df)
    print("\n--- Performance Statistics (grouped by URL) ---")
    print(stats)
    print("-------------------------------------------------")

    # Generate and save plot
    plot_path = os.path.join(output_dir, "performance_over_time.png")
    plot_metrics_over_time(df, plot_path)


if __name__ == '__main__':
    # To test this module, you need a database file.
    # You can generate one by running the monitor first:
    # python3 -m firefly.main monitor
    #
    # Then run this script.

    # Assuming 'firefly_metrics.db' exists from a monitor run
    DB_FILE = "firefly_metrics.db"
    if not os.path.exists(DB_FILE):
        print(f"Database file '{DB_FILE}' not found.")
        print("Please run the monitor first to generate some data.")
    else:
        generate_report(DB_FILE)
