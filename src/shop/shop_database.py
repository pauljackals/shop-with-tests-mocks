import requests


class ShopDatabase:
    def __init__(self, api_url):
        self.api_url = api_url
        self.request = requests.request
