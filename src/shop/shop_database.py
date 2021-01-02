import requests
import re


class ShopDatabase:
    def __init__(self, api_url):
        if type(api_url) != str or not re.match(r"(https?://(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?://(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", api_url):
            raise TypeError("Api URL must be a valid url string")
        else:
            self.api_url = api_url
            self.request = requests.request

    def client_get(self, id_client=None):
        if id_client is not None and type(id_client) != int:
            raise TypeError("Client ID must an integer")
        else:
            try:
                response = self.request('get', self.api_url + '/clients/' + ('' if id_client is None else str(id_client)))
                if response.status_code == 404:
                    raise LookupError("Client with such ID doesn't exist")
                else:
                    return response.json()
            except requests.RequestException:
                suffix = id_client is None and 's' or ''
                raise ConnectionError("Can't get client" + suffix + " from database")

    def client_post(self, name_first, name_last, email):
        if type(name_first) != str or name_first == '' or type(name_last) != str or name_last == '':
            raise TypeError("Both names must be non-empty strings")
        else:
            response = self.request('post', self.api_url + '/clients/', data={
                'name_first': name_first,
                'name_last': name_last,
                'email': email
            })
            return response.json()
