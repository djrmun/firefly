import pycurl
from io import BytesIO
import certifi

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

    try:
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        # Follow redirects
        c.setopt(c.FOLLOWLOCATION, True)
        # Set a timeout
        c.setopt(c.TIMEOUT, 30)

        # Add proxy support
        if proxy_url:
            c.setopt(c.PROXY, proxy_url)
            # You might need to set PROXYTYPE if it's not a standard HTTP proxy
            # c.setopt(c.PROXYTYPE, c.PROXYTYPE_HTTP)

        # For HTTPS, you might need to specify CA certificates
        c.setopt(c.CAINFO, certifi.where())

        c.perform()

        # Get performance metrics
        metrics = {
            'url': url,
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
        # Handle exceptions (e.g., connection errors)
        return {
            'url': url,
            'error': str(e),
        }
    finally:
        c.close()

if __name__ == '__main__':
    # A simple test to run when the script is executed directly
    test_url = "https://www.google.com"
    print(f"Testing with URL: {test_url}")
    metrics = measure_request(test_url)
    import json
    print(json.dumps(metrics, indent=2))

    # Example with a proxy (this will likely fail without a running proxy)
    # test_proxy = "http://127.0.0.1:8080"
    # print(f"\\nTesting with URL: {test_url} and proxy: {test_proxy}")
    # metrics_proxy = measure_request(test_url, proxy_url=test_proxy)
    # print(json.dumps(metrics_proxy, indent=2))
