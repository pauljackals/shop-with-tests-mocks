import unittest
from src.shop.shop_database import ShopDatabase
from unittest.mock import Mock
import requests


class TestShopDatabase(unittest.TestCase):
    def setUp(self):
        self.database = {
            'clients': [
                {
                    'id': 0,
                    'name_first': 'John',
                    'name_last': 'Rose',
                    'email': 'john_rose@example.com'
                },
                {
                    'id': 1,
                    'name_first': 'Jane',
                    'name_last': 'Blue',
                    'email': 'jane_blue@example.com'
                }
            ],
            'items': [
                {
                    'id': 0,
                    'name': 'PlayStation 4 Slim',
                    'value': 1288.00
                },
                {
                    'id': 1,
                    'name': 'Xbox One S',
                    'value': 1049.99
                },
                {
                    'id': 2,
                    'name': 'Nintendo Switch',
                    'value': 1479.00
                }
            ]
        }

        def get_new_id(key):
            new_id = -1
            for entity in self.database[key]:
                if entity['id'] > new_id:
                    new_id = entity['id']
            return new_id + 1

        def request_custom(method, url, data=None):
            url_split = url.split('/')
            endpoint = url_split[-2]
            id_param = None if url_split[-1] == '' else int(url_split[-1])
            if method == 'get' or method == 'delete':
                if id_param is None:
                    return TestResponse(self.database[endpoint], 200)
                else:
                    for entity in self.database[endpoint]:
                        if entity['id'] == id_param:
                            return TestResponse(entity, 200)
                    return TestResponse({}, 404)
            elif method == 'post':
                if endpoint == 'clients':
                    for entity in self.database[endpoint]:
                        if entity['email'] == data['email']:
                            return TestResponse({}, 409)
                return TestResponse({
                    'id': get_new_id(endpoint),
                    **data
                }, 201)
            elif method == 'put' or method == 'patch':
                if endpoint == 'clients' and 'email' in data:
                    for entity in self.database[endpoint]:
                        if entity['email'] == data['email'] and entity['id'] != id_param:
                            return TestResponse({}, 409)
                for entity in self.database[endpoint]:
                    if entity['id'] == id_param:
                        return TestResponse({
                            **entity,
                            **data
                        }, 200)
                return TestResponse({}, 404)

        self.api_url = 'http://example.com'
        self.get_new_id = get_new_id
        self.shop_database = ShopDatabase(self.api_url)
        self.shop_database.request = Mock()
        self.shop_database.request.side_effect = request_custom

    def test_init(self):
        self.assertIsInstance(self.shop_database, ShopDatabase)

    def test_init_wrong_type(self):
        with self.assertRaisesRegex(TypeError, "^Api URL must be a string$"):
            ShopDatabase(545)

    def test_init_invalid(self):
        with self.assertRaisesRegex(ValueError, "^Api URL must be a valid url$"):
            ShopDatabase('http://examplecom')

    def test_client_get(self):
        id_client = 1
        self.assertDictEqual(self.shop_database.client_get(id_client), self.database['clients'][id_client])

    def test_client_get_wrong_type(self):
        with self.assertRaisesRegex(TypeError, "^Client ID must be an integer$"):
            self.shop_database.client_get('1')

    def test_client_get_missing(self):
        with self.assertRaisesRegex(LookupError, "^Client with such ID doesn't exist$"):
            self.shop_database.client_get(999)

    def test_client_get_connection_error(self):
        self.shop_database.request.side_effect = requests.ConnectionError
        with self.assertRaisesRegex(ConnectionError, "^Can't get client from database$"):
            self.shop_database.client_get(1)

    def test_client_get_mock_check(self):
        id_client = 0
        self.shop_database.client_get(id_client)
        self.shop_database.request.assert_called_once_with('get', self.api_url + '/clients/' + str(id_client))

    def test_clients_get(self):
        self.assertListEqual(self.shop_database.client_get(), self.database['clients'])

    def test_clients_get_connection_error(self):
        self.shop_database.request.side_effect = requests.ConnectionError
        with self.assertRaisesRegex(ConnectionError, "^Can't get clients from database$"):
            self.shop_database.client_get()

    def test_clients_get_mock_check(self):
        self.shop_database.client_get()
        self.shop_database.request.assert_called_once_with('get', self.api_url + '/clients/')

    def test_client_post(self):
        client_new = {
            'name_first': 'Harry',
            'name_last': 'Red',
            'email': 'harry_red@example.com'
        }
        self.assertDictEqual(self.shop_database.client_post(**client_new), {
            'id': self.get_new_id('clients'),
            **client_new
        })

    def test_client_post_wrong_type_name(self):
        with self.assertRaisesRegex(TypeError, "^Names and email must be strings$"):
            self.shop_database.client_post(434, 'Red', 'harry_red@example.com')

    def test_client_post_empty_name(self):
        with self.assertRaisesRegex(ValueError, "^Both names must be non-empty$"):
            self.shop_database.client_post('Harry', '', 'harry_red@example.com')

    def test_client_post_wrong_type_email(self):
        with self.assertRaisesRegex(TypeError, "^Names and email must be strings$"):
            self.shop_database.client_post('Harry', 'Red', 654)

    def test_client_post_invalid_email(self):
        with self.assertRaisesRegex(ValueError, "^Email must be valid$"):
            self.shop_database.client_post('Harry', 'Red', 'harry_red@examplecom')

    def test_client_post_connection_error(self):
        self.shop_database.request.side_effect = requests.ConnectionError
        with self.assertRaisesRegex(ConnectionError, "^Can't post client to database$"):
            self.shop_database.client_post('Harry', 'Red', 'harry_red@example.com')

    def test_client_post_non_unique_email(self):
        with self.assertRaisesRegex(ValueError, "^Can't post this client \\(email must be unique\\)$"):
            self.shop_database.client_post('Harry', 'Red', 'jane_blue@example.com')

    def test_client_post_mock_check(self):
        client_new = {
            'name_first': 'Harry',
            'name_last': 'Red',
            'email': 'harry_red@example.com'
        }
        self.shop_database.client_post(**client_new)
        self.shop_database.request.assert_called_once_with('post', self.api_url + '/clients/', data=client_new)

    def test_client_delete(self):
        id_client = 1
        self.assertDictEqual(self.shop_database.client_delete(id_client), self.database['clients'][id_client])

    def test_client_delete_wrong_type(self):
        with self.assertRaisesRegex(TypeError, "^Client ID must be an integer$"):
            self.shop_database.client_delete('1')

    def test_client_delete_missing(self):
        with self.assertRaisesRegex(LookupError, "^Client with such ID doesn't exist$"):
            self.shop_database.client_delete(999)

    def test_client_delete_connection_error(self):
        self.shop_database.request.side_effect = requests.ConnectionError
        with self.assertRaisesRegex(ConnectionError, "^Can't delete client from database$"):
            self.shop_database.client_delete(1)

    def test_client_delete_mock_check(self):
        id_client = 0
        self.shop_database.client_delete(id_client)
        self.shop_database.request.assert_called_once_with('delete', self.api_url + '/clients/' + str(id_client))

    def test_client_put(self):
        client_updated = {
            'id': 1,
            'name_first': 'Harry',
            'name_last': 'Red',
            'email': 'harry_red@example.com'
        }
        self.assertDictEqual(self.shop_database.client_put_patch(*client_updated.values()), client_updated)

    def test_client_put_wrong_type_name(self):
        with self.assertRaisesRegex(TypeError, "^Names and email must be strings$"):
            self.shop_database.client_put_patch(1, 'Harry', 434, 'harry_red@example.com')

    def test_client_put_empty_name(self):
        with self.assertRaisesRegex(ValueError, "^Both names must be non-empty$"):
            self.shop_database.client_put_patch(1, '', 'Red', 'harry_red@example.com')

    def test_client_put_wrong_type_id(self):
        with self.assertRaisesRegex(TypeError, "^Client ID must be an integer$"):
            self.shop_database.client_put_patch('1', 'Harry', 'Red', 'harry_red@example.com')

    def test_client_put_invalid_email(self):
        with self.assertRaisesRegex(ValueError, "^Email must be valid$"):
            self.shop_database.client_put_patch(1, 'Harry', 'Red', 'harry_red@examplecom')

    def test_client_put_missing(self):
        with self.assertRaisesRegex(LookupError, "^Client with such ID doesn't exist$"):
            self.shop_database.client_put_patch(999, 'Harry', 'Red', 'harry_red@example.com')

    def test_client_put_connection_error(self):
        self.shop_database.request.side_effect = requests.ConnectionError
        with self.assertRaisesRegex(ConnectionError, "^Can't put client in database$"):
            self.shop_database.client_put_patch(1, 'Harry', 'Red', 'harry_red@example.com')

    def test_client_put_non_unique_email(self):
        with self.assertRaisesRegex(ValueError, "^Can't put this client \\(email must be unique\\)$"):
            self.shop_database.client_put_patch(1, 'Harry', 'Red', 'john_rose@example.com')

    def test_client_put_old_email(self):
        client_updated = {
            'id': 1,
            'name_first': 'Harry',
            'name_last': 'Red',
            'email': 'jane_blue@example.com'
        }
        self.assertDictEqual(self.shop_database.client_put_patch(*client_updated.values()), client_updated)

    def test_client_put_mock_check(self):
        client_updated_id = 1
        client_updated = {
            'name_first': 'Harry',
            'name_last': 'Red',
            'email': 'harry_red@example.com'
        }
        self.shop_database.client_put_patch(client_updated_id, **client_updated)
        self.shop_database.request.assert_called_once_with('put', self.api_url + '/clients/' + str(client_updated_id), data=client_updated)

    def test_client_patch(self):
        client = self.database['clients'][0]
        client_updated = {
            'id': client['id'],
            'name_first': client['name_first'],
            'name_last': 'Yellow',
            'email': client['email']
        }
        self.assertDictEqual(self.shop_database.client_put_patch(client_updated['id'], name_last=client_updated['name_last']), client_updated)

    def test_client_patch_mock_check(self):
        client_updated_id = 1
        client_updated = {
            'name_last': 'Yellow'
        }
        self.shop_database.client_put_patch(client_updated_id, name_last=client_updated['name_last'])
        self.shop_database.request.assert_called_once_with('patch', self.api_url + '/clients/' + str(client_updated_id), data=client_updated)

    def test_client_patch_no_arguments(self):
        with self.assertRaisesRegex(AttributeError, "^Patch must have at least one attribute$"):
            self.shop_database.client_put_patch(1)

    def test_client_patch_non_unique_email(self):
        with self.assertRaisesRegex(ValueError, "^Can't patch this client \\(email must be unique\\)$"):
            self.shop_database.client_put_patch(1, email='john_rose@example.com')

    def test_client_patch_connection_error(self):
        self.shop_database.request.side_effect = requests.ConnectionError
        with self.assertRaisesRegex(ConnectionError, "^Can't patch client in database$"):
            self.shop_database.client_put_patch(1, email='harry_red@example.com')

    def test_items_get(self):
        self.assertListEqual(self.shop_database.item_get(), self.database['items'])

    def test_item_get(self):
        item = self.database['items'][0]
        self.assertDictEqual(self.shop_database.item_get(item['id']), item)

    def test_item_get_wrong_type(self):
        with self.assertRaisesRegex(TypeError, "^Item ID must be an integer$"):
            self.shop_database.item_get('0')

    def test_item_get_missing(self):
        with self.assertRaisesRegex(LookupError, "^Item with such ID doesn't exist$"):
            self.shop_database.item_get(999)

    def test_items_get_connection_error(self):
        self.shop_database.request.side_effect = requests.ConnectionError
        with self.assertRaisesRegex(ConnectionError, "^Can't get items from database$"):
            self.shop_database.item_get()

    def test_item_get_connection_error(self):
        self.shop_database.request.side_effect = requests.ConnectionError
        with self.assertRaisesRegex(ConnectionError, "^Can't get item from database$"):
            self.shop_database.item_get(0)

    def test_items_get_mock_check(self):
        self.shop_database.item_get()
        self.shop_database.request.assert_called_once_with('get', self.api_url + '/items/')

    def test_item_get_mock_check(self):
        id_item = 0
        self.shop_database.item_get(id_item)
        self.shop_database.request.assert_called_once_with('get', self.api_url + '/items/' + str(id_item))

    def test_item_post(self):
        item_new = {
            'name': 'PlayStation 5',
            'value': 2199.99
        }
        self.assertDictEqual(self.shop_database.item_post(**item_new), {
            'id': self.get_new_id('items'),
            **item_new
        })

    def test_item_post_wrong_type_name(self):
        with self.assertRaisesRegex(TypeError, "^Name must be a string$"):
            self.shop_database.item_post(434, 2199.99)

    def test_item_post_wrong_type_value(self):
        with self.assertRaisesRegex(TypeError, "^Value must be a float$"):
            self.shop_database.item_post('PlayStation 5', 2199)

    def test_item_post_empty_name(self):
        with self.assertRaisesRegex(ValueError, "^Name must not be empty$"):
            self.shop_database.item_post('', 2199.99)

    def test_item_post_more_than_2_decimal(self):
        with self.assertRaisesRegex(ValueError, "^Value must have no more than 2 decimal places$"):
            self.shop_database.item_post('PlayStation 5', 2199.993)

    def test_item_post_connection_error(self):
        self.shop_database.request.side_effect = requests.ConnectionError
        with self.assertRaisesRegex(ConnectionError, "^Can't post item to database$"):
            self.shop_database.item_post('PlayStation 5', 2199.99)

    def tearDown(self):
        self.shop_database = None
        self.api_url = None
        self.get_new_id = None
        self.shop_database = None


class TestResponse:
    def __init__(self, value, status_code):
        self.value = value
        self.status_code = status_code

    def json(self):
        return self.value


if __name__ == '__main__':
    unittest.main()
