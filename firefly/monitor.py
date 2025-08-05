import pycurl
from io import BytesIO
import certifi
import socket
import psutil

def get_interface_for_ip(ip_address: str) -> str:
    """
    Finds the network interface name for a given local IP address.

    Args:
        ip_address: The local IP address.

    Returns:
        The name of the network interface, or 'unknown' if not found.
    """
    if not ip_address:
        return 'unknown'

    try:
        all_interfaces = psutil.net_if_addrs()
        for interface_name, addresses in all_interfaces.items():
            for addr in addresses:
                if addr.address == ip_address:
                    return interface_name
    except Exception:
        # psutil might fail on some platforms or in some environments
        return 'error'

    return 'unknown'


def measure_request(url: str, proxy_url: str = None):
    """
    Measures the performance of a single HTTP GET request to the given URL.

    Args:
        url: The URL to request.
        proxy_url: The proxy URL to use for the request.

    Returns:
        A dictionary containing the performance metrics.
    """
    c = pycurl.Curl()
    buffer = BytesIO()

    hostname = socket.gethostname()
    network_interface = 'unknown'

    try:
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.FOLLOWLOCATION, True)
        c.setopt(c.TIMEOUT, 30)

        if proxy_url:
            c.setopt(c.PROXY, proxy_url)

        c.setopt(c.CAINFO, certifi.where())

        c.perform()

        # Get the local IP address used for the connection
        local_ip = c.getinfo(pycurl.LOCAL_IP)
        network_interface = get_interface_for_ip(local_ip)

        metrics = {
            'url': url,
            'hostname': hostname,
            'network_interface': network_interface,
            'http_code': c.getinfo(pycurl.HTTP_CODE),
            'time_namelookup': c.getinfo(pycurl.NAMELOOKUP_TIME),
            'time_connect': c.getinfo(pycurl.CONNECT_TIME),
            'time_appconnect': c.getinfo(pycurl.APPCONNECT_TIME),
            'time_pretransfer': c.getinfo(pycurl.PRETRANSFER_TIME),
            'time_starttransfer': c.getinfo(pycurl.STARTTRANSFER_TIME),
            'time_total': c.getinfo(pycurl.TOTAL_TIME),
            'speed_download': c.getinfo(pycurl.SPEED_DOWNLOAD),
            'speed_upload': c.getinfo(pycurl.SPEED_UPLOAD),
            'size_download': c.getinfo(pycurl.SIZE_DOWNLOAD),
        }

        return metrics

    except pycurl.error as e:
        return {
            'url': url,
            'hostname': hostname,
            'network_interface': network_interface,
            'error': str(e),
        }
    finally:
        c.close()

if __name__ == '__main__':
    # Test the updated monitor script
    test_url = "https://www.google.com"
    print(f"Testing with URL: {test_url}")
    metrics = measure_request(test_url)
    import json
    print(json.dumps(metrics, indent=2))
