import requests
import re


class ShopDatabase:
    def __init__(self, api_url):
        if type(api_url) != str or not re.match(r"(https?://(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?://(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", api_url):
            raise TypeError("Api URL must be a valid url string")
        else:
            self.api_url = api_url
            self.request = requests.request

    def client_get(self, id_client):
        if type(id_client) != int:
            raise TypeError("Client ID must an integer")
        else:
            try:
                response = self.request('get', self.api_url + '/clients/' + str(id_client))
                if response.status_code == 404:
                    raise LookupError("Client with such ID doesn't exist")
                else:
                    return response.json()
            except requests.RequestException:
                raise ConnectionError("Can't get client from database")

    def clients_get(self):
        try:
            response = self.request('get', self.api_url + '/clients/')
            return response.json()
        except requests.RequestException:
            raise ConnectionError("Can't get clients from database")
