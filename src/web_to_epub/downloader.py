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

    def get(self, url):
        """
        Fetches the content of a given URL.
        """
        if self.delay > 0:
            time.sleep(self.delay / 1000.0)

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
