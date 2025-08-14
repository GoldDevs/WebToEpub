import requests

def get_html(url: str) -> str:
    """
    Fetches the HTML content of a given URL.

    :param url: The URL to fetch.
    :return: The HTML content as a string.
    :raises: requests.exceptions.RequestException for connection errors.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        raise
