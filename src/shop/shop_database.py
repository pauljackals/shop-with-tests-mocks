import requests
import re


class ShopDatabase:
    def __init__(self, api_url):
        if type(api_url) != str:
            raise TypeError("Api URL must be a string")
        elif not re.match(r"(https?://(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?://(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", api_url):
            raise ValueError("Api URL must be a valid url")
        else:
            self.api_url = api_url
            self.request = requests.request

    @staticmethod
    def __email_invalid(email):
        return not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email)

    @staticmethod
    def __entity_get(request, api_url, endpoint, word, id_entity=None):
        if id_entity is not None and type(id_entity) != int:
            raise TypeError(word.capitalize() + " ID must be an integer")
        else:
            try:
                response = request('get', api_url + '/' + endpoint + '/' + ('' if id_entity is None else str(id_entity)))
                if response.status_code == 404:
                    raise LookupError(word.capitalize() + " with such ID doesn't exist")
                else:
                    return response.json()
            except requests.RequestException:
                suffix = id_entity is None and 's' or ''
                raise ConnectionError("Can't get " + word + suffix + " from database")

    def client_get(self, id_client=None):
        return self.__entity_get(self.request, self.api_url, 'clients', 'client', id_client)
        # if id_client is not None and type(id_client) != int:
        #     raise TypeError("Client ID must be an integer")
        # else:
        #     try:
        #         response = self.request('get', self.api_url + '/clients/' + ('' if id_client is None else str(id_client)))
        #         if response.status_code == 404:
        #             raise LookupError("Client with such ID doesn't exist")
        #         else:
        #             return response.json()
        #     except requests.RequestException:
        #         suffix = id_client is None and 's' or ''
        #         raise ConnectionError("Can't get client" + suffix + " from database")

    def client_post(self, name_first, name_last, email):
        if type(name_first) != str or type(name_last) != str or type(email) != str:
            raise TypeError("Names and email must be strings")
        elif name_first == '' or name_last == '':
            raise ValueError("Both names must be non-empty")
        elif self.__email_invalid(email):
            raise ValueError("Email must be valid")
        else:
            try:
                response = self.request('post', self.api_url + '/clients/', data={
                    'name_first': name_first,
                    'name_last': name_last,
                    'email': email
                })
                if response.status_code == 409:
                    raise ValueError("Can't post this client (email must be unique)")
                else:
                    return response.json()
            except requests.RequestException:
                raise ConnectionError("Can't post client to database")

    def client_delete(self, id_client):
        if type(id_client) != int:
            raise TypeError("Client ID must be an integer")
        else:
            try:
                response = self.request('delete', self.api_url + '/clients/' + str(id_client))
                if response.status_code == 404:
                    raise LookupError("Client with such ID doesn't exist")
                else:
                    return response.json()
            except requests.RequestException:
                raise ConnectionError("Can't delete client from database")

    def client_put_patch(self, id_client, name_first=None, name_last=None, email=None):
        if name_first == name_last == email is None:
            raise AttributeError("Patch must have at least one attribute")
        elif type(id_client) != int:
            raise TypeError("Client ID must be an integer")
        elif (name_first is not None and type(name_first) != str) or (name_last is not None and type(name_last) != str) or (email is not None and type(email) != str):
            raise TypeError("Names and email must be strings")
        elif name_first == '' or name_last == '':
            raise ValueError("Both names must be non-empty")
        elif email is not None and self.__email_invalid(email):
            raise ValueError("Email must be valid")
        else:
            method = 'patch' if None in [name_first, name_last, email] else 'put'
            try:
                response = self.request(method, self.api_url + '/clients/' + str(id_client), data={
                    **({} if name_first is None else {'name_first': name_first}),
                    **({} if name_last is None else {'name_last': name_last}),
                    **({} if email is None else {'email': email})
                })
                if response.status_code == 404:
                    raise LookupError("Client with such ID doesn't exist")
                elif response.status_code == 409:
                    raise ValueError("Can't " + method + " this client (email must be unique)")
                else:
                    return response.json()
            except requests.RequestException:
                raise ConnectionError("Can't " + method + " client in database")

    def item_get(self, id_item=None):
        return self.__entity_get(self.request, self.api_url, 'items', 'item', id_item)
        # if id_item is not None and type(id_item) != int:
        #     raise TypeError("Item ID must be an integer")
        # else:
        #     try:
        #         response = self.request('get', self.api_url + '/items/' + ('' if id_item is None else str(id_item)))
        #         if response.status_code == 404:
        #             raise LookupError("Item with such ID doesn't exist")
        #         else:
        #             return response.json()
        #     except requests.RequestException:
        #         suffix = id_item is None and 's' or ''
        #         raise ConnectionError("Can't get item" + suffix + " from database")

    def item_post(self, name, value):
        if type(name) != str:
            raise TypeError("Name must be a string")
        else:
            response = self.request('post', self.api_url + '/items/', data={
                'name': name,
                'value': value
            })
            return response.json()
