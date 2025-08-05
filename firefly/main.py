import time
import schedule
import logging
import argparse
from firefly import config, monitor, storage, analysis

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_monitoring_loop():
    """
    Main function to run the monitoring scheduler.
    """
    logging.info("Starting Firefly Network Performance Monitor...")

    # Load configuration
    app_config = config.load_config()
    urls = config.get_urls(app_config)
    interval = config.get_schedule_interval(app_config)
    db_path = config.get_database_path(app_config)
    proxy_config = config.get_proxy_config(app_config)

    if not urls:
        logging.error("No URLs found in the configuration. Exiting.")
        return

    # Initialize the database
    logging.info(f"Initializing database at '{db_path}'...")
    storage.init_db(db_path)
    logging.info("Database initialized.")

    logging.info(f"Scheduling checks to run every {interval} seconds.")

    # Schedule the job
    schedule.every(interval).seconds.do(
        perform_checks,
        db_path=db_path,
        urls=urls,
        proxy_config=proxy_config
    )

    # Run the job once immediately
    perform_checks(db_path=db_path, urls=urls, proxy_config=proxy_config)

    # Run the scheduler loop
    while True:
        schedule.run_pending()
        time.sleep(1)

def perform_checks(db_path: str, urls: list, proxy_config: dict = None):
    """
    Performs the monitoring checks for all configured URLs.
    """
    logging.info(f"Starting new round of checks for {len(urls)} URLs...")

    proxy_url = None
    if proxy_config:
        proxy_url = proxy_config.get("http") or proxy_config.get("https")

    for url in urls:
        logging.info(f"Measuring request to {url}" + (f" via proxy {proxy_url}" if proxy_url else ""))
        metrics = monitor.measure_request(url, proxy_url=proxy_url)

        if "error" in metrics:
            logging.error(f"Failed to measure {url}: {metrics['error']}")
        else:
            logging.info(f"Successfully measured {url}, total time: {metrics['time_total']:.4f}s")

        storage.insert_metric(db_path, metrics)

    logging.info("Finished round of checks.")

def run_analysis():
    """
    Runs the data analysis and generates a report.
    """
    logging.info("Starting Firefly data analysis...")
    app_config = config.load_config()
    db_path = config.get_database_path(app_config)

    analysis.generate_report(db_path)


def main():
    """
    Main entry point for the Firefly CLI.
    """
    parser = argparse.ArgumentParser(description="Firefly Network Performance Monitor")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # 'monitor' command
    monitor_parser = subparsers.add_parser("monitor", help="Start the network performance monitor")
    monitor_parser.set_defaults(func=run_monitoring_loop)

    # 'analyze' command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze the collected performance data")
    analyze_parser.set_defaults(func=run_analysis)

    args = parser.parse_args()
    args.func()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting Firefly.")
