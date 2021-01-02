import requests
import re


class ShopDatabase:
    def __init__(self, api_url):
        if type(api_url) != str or not re.match(r"(https?://(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?://(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", api_url):
            raise TypeError("Api URL must be a valid url string")
        else:
            self.api_url = api_url
            self.request = requests.request
