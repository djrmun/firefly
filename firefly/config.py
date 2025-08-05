import yaml
from typing import Dict, Any, List

DEFAULT_CONFIG_PATH = "config.yml"

def load_config(path: str = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    """
    Loads the configuration from a YAML file.

    Args:
        path: The path to the configuration file.

    Returns:
        A dictionary containing the configuration.
    """
    try:
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file not found at '{path}'.")
        print(f"Please create a '{path}' file or copy 'config.yml.example'.")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file '{path}': {e}")
        exit(1)

def get_urls(config: Dict[str, Any]) -> List[str]:
    """Returns the list of URLs from the config."""
    return config.get("urls", [])

def get_schedule_interval(config: Dict[str, Any]) -> int:
    """Returns the schedule interval in seconds from the config."""
    return config.get("schedule", {}).get("interval_seconds", 60)

def get_database_path(config: Dict[str, Any]) -> str:
    """Returns the database file path from the config."""
    return config.get("database", {}).get("file", "firefly_metrics.db")

def get_proxy_config(config: Dict[str, Any]) -> Dict[str, str]:
    """Returns the proxy configuration."""
    return config.get("proxy")


if __name__ == '__main__':
    # To test this module, first create a 'config.yml' by copying 'config.yml.example'
    # cp config.yml.example config.yml
    print("Testing config loading...")
    config = load_config()
    if config:
        print("Config loaded successfully:")
        import json
        print(json.dumps(config, indent=2))
        print("\\n--- Parsed values ---")
        print(f"URLs: {get_urls(config)}")
        print(f"Schedule Interval: {get_schedule_interval(config)}s")
        print(f"Database Path: {get_database_path(config)}")
        print(f"Proxy Config: {get_proxy_config(config)}")
