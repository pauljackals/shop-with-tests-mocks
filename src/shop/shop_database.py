import requests


class ShopDatabase:
    def __init__(self, api_url):
        if type(api_url) != str:
            raise TypeError("Api URL must be a valid url string")
        else:
            self.api_url = api_url
            self.request = requests.request
