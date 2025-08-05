# Firefly - Network Performance Monitor

Firefly is a Python-based tool for monitoring the performance of HTTP/S requests. It is designed to help diagnose network bottlenecks, such as those caused by proxies or firewalls, by periodically measuring request performance to a configurable set of URLs and storing the results for analysis.

## Features

- **Configurable Monitoring:** Specify a list of URLs and a monitoring interval in a simple `config.yml` file.
- **Detailed Metrics:** Captures key performance indicators for each request, similar to cURL's detailed output, including:
    - `time_total`: Total transaction time
    - `time_namelookup`: Time to resolve the hostname
    - `time_connect`: Time to establish the TCP connection
    - `time_starttransfer`: Time until the first byte is received
- **Persistent Storage:** All metrics are stored in an SQLite database for historical analysis.
- **Proxy Support:** Can route requests through an HTTP/S proxy.
- **Data Analysis & Visualization:** Includes a command to analyze the collected data, calculating statistics (min, max, mean, 95th percentile) and generating plots of performance over time.

## Installation

1.  Clone this repository.
2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Copy the example configuration file:
    ```bash
    cp config.yml.example config.yml
    ```
2.  Edit `config.yml` to suit your needs:
    - **`urls`**: A list of the URLs you want to monitor.
    - **`schedule.interval_seconds`**: How often, in seconds, to run the performance checks.
    - **`database.file`**: The name of the SQLite database file where metrics will be stored.
    - **`proxy`** (optional): If you need to use a proxy, you can specify the `http` and `https` proxy URLs here.

## Usage

The tool has two main commands: `monitor` and `analyze`.

### Start the Monitor

To start the monitoring process, run the following command. It will run continuously in the foreground, performing checks at the interval you configured.

```bash
python3 -m firefly.main monitor
```

Press `Ctrl+C` to stop the monitor.

### Analyze Collected Data

To analyze the data collected by the monitor, run the `analyze` command:

```bash
python3 -m firefly.main analyze
```

This will:
1.  Print a table of performance statistics (mean, min, max, 95th percentile) to the console, grouped by URL.
2.  Generate a plot of the total request time over time for each URL and save it as `reports/performance_over_time.png`.

## Proving a Bottleneck

The primary goal of this tool is to compare network performance across different environments. To prove a bottleneck, you can:

1.  Run the monitor in one environment (e.g., a home network with a direct internet connection) for a period of time to establish a baseline.
2.  Run the monitor again in a different environment (e.g., a corporate network behind a proxy and firewall), using the same `config.yml`.
3.  Use the `analyze` command in each environment to generate reports.
4.  Compare the statistics and plots from both environments. A significant increase in `time_connect` or `time_starttransfer` in the corporate environment could indicate a proxy or firewall bottleneck.
