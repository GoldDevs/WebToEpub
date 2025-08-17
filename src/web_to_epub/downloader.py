"""
This module contains the Downloader class for fetching web page content.
"""
import requests
import time

class Downloader:
    def __init__(self, delay=0):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.delay = delay # in milliseconds

    def get(self, url, num_retries=3):
        """
        Fetches the content of a given URL with retries and rate-limiting.
        """
        if self.delay > 0:
            time.sleep(self.delay / 1000.0)

        for attempt in range(num_retries):
            try:
                response = self.session.get(url, timeout=10)

                if response.status_code == 429: # Too Many Requests
                    retry_after = int(response.headers.get("Retry-After", 5))
                    print(f"Rate limited. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue

                response.raise_for_status()
                return response.text

            except requests.exceptions.RequestException as e:
                print(f"Error fetching {url} (attempt {attempt+1}/{num_retries}): {e}")
                if attempt < num_retries - 1:
                    # Exponential backoff
                    backoff_time = 2 ** attempt
                    print(f"Retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)
                else:
                    print(f"Failed to fetch {url} after {num_retries} attempts.")
                    raise e # Re-raise the exception to be handled by the caller
        return None

    def post(self, url, data, num_retries=3):
        """
        Sends a POST request with JSON data, with retries and rate-limiting.
        """
        if self.delay > 0:
            time.sleep(self.delay / 1000.0)

        for attempt in range(num_retries):
            try:
                response = self.session.post(url, json=data, timeout=10)

                if response.status_code == 429: # Too Many Requests
                    retry_after = int(response.headers.get("Retry-After", 5))
                    print(f"Rate limited. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue

                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                print(f"Error posting to {url} (attempt {attempt+1}/{num_retries}): {e}")
                if attempt < num_retries - 1:
                    backoff_time = 2 ** attempt
                    print(f"Retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)
                else:
                    print(f"Failed to post to {url} after {num_retries} attempts.")
                    raise e
        return None
