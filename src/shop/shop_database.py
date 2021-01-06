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
    def __entity_get(request, api_url, endpoint, word, id_entity):
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

    @staticmethod
    def __entity_delete(request, api_url, endpoint, word, id_entity):
        if type(id_entity) != int:
            raise TypeError(word.capitalize() + " ID must be an integer")
        else:
            try:
                response = request('delete', api_url + '/' + endpoint + '/' + str(id_entity))
                if response.status_code == 404:
                    raise LookupError(word.capitalize() + " with such ID doesn't exist")
                else:
                    return response.json()
            except requests.RequestException:
                raise ConnectionError("Can't delete " + word + " from database")

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
        return self.__entity_delete(self.request, self.api_url, 'clients', 'client', id_client)
        # if type(id_client) != int:
        #     raise TypeError("Client ID must be an integer")
        # else:
        #     try:
        #         response = self.request('delete', self.api_url + '/clients/' + str(id_client))
        #         if response.status_code == 404:
        #             raise LookupError("Client with such ID doesn't exist")
        #         else:
        #             return response.json()
        #     except requests.RequestException:
        #         raise ConnectionError("Can't delete client from database")

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
        elif type(value) != float:
            raise TypeError("Value must be a float")
        elif name == '':
            raise ValueError("Name must not be empty")
        elif len(str(value).split('.')[1]) > 2:
            raise ValueError("Value must have no more than 2 decimal places")
        else:
            try:
                response = self.request('post', self.api_url + '/items/', data={
                    'name': name,
                    'value': value
                })
                return response.json()
            except requests.RequestException:
                raise ConnectionError("Can't post item to database")

    def item_delete(self, id_item):
        return self.__entity_delete(self.request, self.api_url, 'items', 'item', id_item)

    def item_put_patch(self, id_item, name=None, value=None):
        if name == value is None:
            raise AttributeError("Patch must have at least one attribute")
        elif type(id_item) != int:
            raise TypeError("Item ID must be an integer")
        elif name is not None and type(name) != str:
            raise TypeError("Name must be a string")
        elif value is not None and type(value) != float:
            raise TypeError("Value must be a float")
        elif name == '':
            raise ValueError("Name must not be empty")
        elif value is not None and len(str(value).split('.')[1]) > 2:
            raise ValueError("Value must have no more than 2 decimal places")
        else:
            method = 'patch' if None in [name, value] else 'put'
            try:
                response = self.request(method, self.api_url + '/items/' + str(id_item), data={
                    **({} if name is None else {'name': name}),
                    **({} if value is None else {'value': value})
                })
                if response.status_code == 404:
                    raise LookupError("Item with such ID doesn't exist")
                else:
                    return response.json()
            except requests.RequestException:
                raise ConnectionError("Can't " + method + " item in database")

    def order_post(self, id_client, ids_items):
        if type(id_client) != int:
            raise TypeError("Client ID must be an integer")
        elif type(ids_items) != list:
            raise TypeError("Items IDs must be a list")
        elif len(ids_items) < 1:
            raise ValueError("Items IDs must not be empty")
        else:
            try:
                for i in ids_items:
                    if type(i) != int:
                        raise TypeError("Items IDs must all be integers")
                response = self.request('post', self.api_url + '/orders/', data={
                    'id_client': id_client,
                    'ids_items': ids_items
                })
                if response.status_code == 404:
                    raise LookupError("Referenced entities don't exist")
                else:
                    return response.json()
            except requests.RequestException:
                raise ConnectionError("Can't post order to database")

    def order_get(self, id_order=None):
        return self.__entity_get(self.request, self.api_url, 'orders', 'order', id_order)

    def order_delete(self, id_order):
        return self.__entity_delete(self.request, self.api_url, 'orders', 'order', id_order)

    def order_put_patch(self, id_order, id_client, ids_items):
        if type(id_order) != int or (type(id_client) != int):
            raise TypeError("Both order and client IDs must be integers")
        elif type(ids_items) != list:
            raise TypeError("Items IDs must be a list")
        elif ids_items is not None and len(ids_items) < 1:
            raise ValueError("Items IDs must not be empty")
        else:
            if ids_items is not None:
                for i in ids_items:
                    if type(i) != int:
                        raise TypeError("Items IDs must all be integers")
            method = 'put'
            response = self.request(method, self.api_url + '/orders/' + str(id_order), data={
                **({'id_client': id_client}),
                **({'ids_items': ids_items})
            })
            return response.json()
