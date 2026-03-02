from urllib.parse import urlparse

def get_host_from_url(url: str):
    parsed_url = urlparse(url)
    host = parsed_url.netloc or parsed_url.path
    return host