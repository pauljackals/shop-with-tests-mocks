import unittest
from src.shop.shop_database import ShopDatabase
from unittest.mock import Mock, MagicMock
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
            ],
            'orders': [
                {
                    'id': 0,
                    'id_client': 0
                },
                {
                    'id': 1,
                    'id_client': 1
                }
            ],
            'orders_items': [
                {
                    'id_item': 2,
                    'id_order': 0
                },
                {
                    'id_item': 1,
                    'id_order': 1
                },
                {
                    'id_item': 0,
                    'id_order': 1
                }
            ]
        }
        self.get_ids_items = lambda id_param: list(map(lambda y: y['id_item'], filter(lambda x: x['id_order'] == id_param, self.database['orders_items'])))

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
                    test_response_data = self.database[endpoint]
                    if endpoint == 'orders':
                        test_response_data = list(map(lambda x: {
                            **x,
                            'ids_items': self.get_ids_items(x['id'])
                        }, test_response_data))
                    return TestResponse(test_response_data, 200)
                else:
                    for entity in self.database[endpoint]:
                        if entity['id'] == id_param:
                            test_response_data = entity
                            if endpoint == 'orders':
                                test_response_data = {
                                    **test_response_data,
                                    'ids_items': self.get_ids_items(id_param)
                                }
                            return TestResponse(test_response_data, 200)
                    return TestResponse({}, 404)
            elif method == 'post':
                if endpoint == 'clients':
                    for entity in self.database[endpoint]:
                        if entity['email'] == data['email']:
                            return TestResponse({}, 409)
                elif endpoint == 'orders':
                    order_correct = False
                    for client in self.database['clients']:
                        if client['id'] == data['id_client']:
                            order_correct = True
                            break
                    if order_correct:
                        ids_items = map(lambda item: item['id'], self.database['items'])
                        for id_item in data['ids_items']:
                            if id_item not in ids_items:
                                order_correct = False
                                break
                    if not order_correct:
                        return TestResponse({}, 404)
                return TestResponse({
                    'id': get_new_id(endpoint),
                    **data
                }, 201)
            elif method == 'put' or method == 'patch':
                if endpoint == 'clients' and 'email' in data:
                    for entity in self.database[endpoint]:
                        if entity['email'] == data['email'] and entity['id'] != id_param:
                            return TestResponse({}, 409)
                elif endpoint == 'orders':
                    order_correct = False
                    if 'id_client' in data:
                        for client in self.database['clients']:
                            if client['id'] == data['id_client']:
                                order_correct = True
                                break
                    else:
                        order_correct = True
                    if order_correct and 'ids_items' in data:
                        ids_items = map(lambda item: item['id'], self.database['items'])
                        for id_item in data['ids_items']:
                            if id_item not in ids_items:
                                order_correct = False
                                break
                    if not order_correct:
                        return TestResponse({}, 404)
                for entity in self.database[endpoint]:
                    if entity['id'] == id_param:
                        test_response_data = entity
                        if endpoint == 'orders':
                            test_response_data = {
                                **test_response_data,
                                'ids_items': self.get_ids_items(id_param)
                            }
                        return TestResponse({
                            **test_response_data,
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
            ShopDatabase(MagicMock(spec=int))

    def test_init_invalid(self):
        with self.assertRaisesRegex(ValueError, "^Api URL must be a valid url$"):
            ShopDatabase('http://examplecom')

    def test_client_get(self):
        id_client = 1
        self.assertDictEqual(self.shop_database.client_get(id_client), self.database['clients'][id_client])

    def test_client_get_wrong_type(self):
        with self.assertRaisesRegex(TypeError, "^Client ID must be an integer$"):
            self.shop_database.client_get(MagicMock(spec=str))

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
            self.shop_database.client_post(MagicMock(spec=int), 'Red', 'harry_red@example.com')

    def test_client_post_empty_name(self):
        with self.assertRaisesRegex(ValueError, "^Both names must be non-empty$"):
            self.shop_database.client_post('Harry', '', 'harry_red@example.com')

    def test_client_post_wrong_type_email(self):
        with self.assertRaisesRegex(TypeError, "^Names and email must be strings$"):
            self.shop_database.client_post('Harry', 'Red', MagicMock(spec=int))

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
            self.shop_database.client_delete(MagicMock(spec=str))

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
            self.shop_database.client_put_patch(1, 'Harry', MagicMock(spec=int), 'harry_red@example.com')

    def test_client_put_empty_name(self):
        with self.assertRaisesRegex(ValueError, "^Both names must be non-empty$"):
            self.shop_database.client_put_patch(1, '', 'Red', 'harry_red@example.com')

    def test_client_put_wrong_type_id(self):
        with self.assertRaisesRegex(TypeError, "^Client ID must be an integer$"):
            self.shop_database.client_put_patch(MagicMock(spec=str), 'Harry', 'Red', 'harry_red@example.com')

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

    def test_item_get_name_check(self):
        item = self.database['items'][0]
        self.assertEqual(self.shop_database.item_get(item['id'])['name'], item['name'])

    def test_item_get_wrong_type(self):
        with self.assertRaisesRegex(TypeError, "^Item ID must be an integer$"):
            self.shop_database.item_get(MagicMock(spec=str))

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
            self.shop_database.item_post(MagicMock(spec=int), 2199.99)

    def test_item_post_wrong_type_value(self):
        with self.assertRaisesRegex(TypeError, "^Value must be a float$"):
            self.shop_database.item_post('PlayStation 5', MagicMock(spec=int))

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

    def test_item_post_mock_check(self):
        item_new = {
            'name': 'PlayStation 5',
            'value': 2199.99,
        }
        self.shop_database.item_post(**item_new)
        self.shop_database.request.assert_called_once_with('post', self.api_url + '/items/', data=item_new)

    def test_item_delete(self):
        item = self.database['items'][0]
        self.assertDictEqual(self.shop_database.item_delete(item['id']), item)

    def test_item_delete_wrong_type(self):
        with self.assertRaisesRegex(TypeError, "^Item ID must be an integer$"):
            self.shop_database.item_delete(MagicMock(spec=str))

    def test_item_delete_missing(self):
        with self.assertRaisesRegex(LookupError, "^Item with such ID doesn't exist$"):
            self.shop_database.item_delete(999)

    def test_item_delete_connection_error(self):
        self.shop_database.request.side_effect = requests.ConnectionError
        with self.assertRaisesRegex(ConnectionError, "^Can't delete item from database$"):
            self.shop_database.item_delete(1)

    def test_item_delete_mock_check(self):
        id_item = 0
        self.shop_database.item_delete(id_item)
        self.shop_database.request.assert_called_once_with('delete', self.api_url + '/items/' + str(id_item))

    def test_item_put(self):
        item_updated = {
            'id': 1,
            'name': 'PlayStation 5',
            'value': 2000.99
        }
        self.assertDictEqual(self.shop_database.item_put_patch(*item_updated.values()), item_updated)

    def test_item_put_wrong_type_name(self):
        with self.assertRaisesRegex(TypeError, "^Name must be a string$"):
            self.shop_database.item_put_patch(1, MagicMock(spec=int), 2000.99)

    def test_item_put_wrong_type_value(self):
        with self.assertRaisesRegex(TypeError, "^Value must be a float$"):
            self.shop_database.item_put_patch(1, 'PlayStation 5', MagicMock(spec=int))

    def test_item_put_empty_name(self):
        with self.assertRaisesRegex(ValueError, "^Name must not be empty$"):
            self.shop_database.item_put_patch(1, '', 2000.99)

    def test_item_put_wrong_type_id(self):
        with self.assertRaisesRegex(TypeError, "^Item ID must be an integer$"):
            self.shop_database.item_put_patch(MagicMock(spec=str), 'PlayStation 5', 2000.99)

    def test_item_put_more_than_2_decimal(self):
        with self.assertRaisesRegex(ValueError, "^Value must have no more than 2 decimal places$"):
            self.shop_database.item_put_patch(1, 'PlayStation 5', 2000.995)

    def test_item_put_missing(self):
        with self.assertRaisesRegex(LookupError, "^Item with such ID doesn't exist$"):
            self.shop_database.item_put_patch(999, 'PlayStation 5', 2000.99)

    def test_item_put_connection_error(self):
        self.shop_database.request.side_effect = requests.ConnectionError
        with self.assertRaisesRegex(ConnectionError, "^Can't put item in database$"):
            self.shop_database.item_put_patch(1, 'PlayStation 5', 2000.99)

    def test_item_put_mock_check(self):
        item_updated_id = 1
        item_updated = {
            'name': 'PlayStation 5',
            'value': 2000.99
        }
        self.shop_database.item_put_patch(item_updated_id, **item_updated)
        self.shop_database.request.assert_called_once_with('put', self.api_url + '/items/' + str(item_updated_id), data=item_updated)

    def test_item_patch(self):
        item = self.database['items'][0]
        item_updated = {
            'id': item['id'],
            'name': 'PlayStation 3',
            'value': item['value']
        }
        self.assertDictEqual(self.shop_database.item_put_patch(item_updated['id'], name=item_updated['name']), item_updated)

    def test_item_patch_mock_check(self):
        item_updated_id = 1
        item_updated = {
            'name': 'PlayStation 3'
        }
        self.shop_database.item_put_patch(item_updated_id, name=item_updated['name'])
        self.shop_database.request.assert_called_once_with('patch', self.api_url + '/items/' + str(item_updated_id), data=item_updated)

    def test_item_patch_no_arguments(self):
        with self.assertRaisesRegex(AttributeError, "^Patch must have at least one attribute$"):
            self.shop_database.item_put_patch(1)

    def test_item_patch_connection_error(self):
        self.shop_database.request.side_effect = requests.ConnectionError
        with self.assertRaisesRegex(ConnectionError, "^Can't patch item in database$"):
            self.shop_database.item_put_patch(1, name='PlayStation 3')

    def test_order_post(self):
        order_new = {
            'id_client': 1,
            'ids_items': [0, 2]
        }
        self.assertDictEqual(self.shop_database.order_post(**order_new), {
            'id': self.get_new_id('orders'),
            **order_new
        })

    def test_order_post_wrong_type_client(self):
        with self.assertRaisesRegex(TypeError, "^Client ID must be an integer$"):
            self.shop_database.order_post(MagicMock(spec=str), [0, 2])

    def test_order_post_wrong_type_items(self):
        with self.assertRaisesRegex(TypeError, "^Items IDs must be a list$"):
            self.shop_database.order_post(1, MagicMock(spec=int))

    def test_order_post_empty_items(self):
        with self.assertRaisesRegex(ValueError, "^Items IDs must not be empty$"):
            self.shop_database.order_post(1, [])

    def test_order_post_wrong_type_items_elements(self):
        with self.assertRaisesRegex(TypeError, "^Items IDs must all be integers$"):
            self.shop_database.order_post(1, [0, MagicMock(spec=str), 2])

    def test_order_post_mock_check(self):
        order_new = {
            'id_client': 1,
            'ids_items': [0, 2],
        }
        self.shop_database.order_post(**order_new)
        self.shop_database.request.assert_called_once_with('post', self.api_url + '/orders/', data=order_new)

    def test_order_post_connection_error(self):
        self.shop_database.request.side_effect = requests.ConnectionError
        with self.assertRaisesRegex(ConnectionError, "^Can't post order to database$"):
            self.shop_database.order_post(1, [0, 2])

    def test_order_post_missing_client(self):
        with self.assertRaisesRegex(LookupError, "^Referenced entities don't exist$"):
            self.shop_database.order_post(999, [0, 2])

    def test_order_post_missing_item(self):
        with self.assertRaisesRegex(LookupError, "^Referenced entities don't exist$"):
            self.shop_database.order_post(1, [0, 999])

    def test_orders_get(self):
        orders = list(map(lambda x: {
            **x,
            'ids_items': self.get_ids_items(x['id'])
        }, self.database['orders']))
        self.assertListEqual(self.shop_database.order_get(), orders)

    def test_order_get(self):
        id_order = 0
        order = {
            **self.database['orders'][id_order],
            'ids_items': self.get_ids_items(id_order)
        }
        self.assertDictEqual(self.shop_database.order_get(order['id']), order)

    def test_order_get_wrong_type(self):
        with self.assertRaisesRegex(TypeError, "^Order ID must be an integer$"):
            self.shop_database.order_get(MagicMock(spec=str))

    def test_order_get_missing(self):
        with self.assertRaisesRegex(LookupError, "^Order with such ID doesn't exist$"):
            self.shop_database.order_get(999)

    def test_orders_get_connection_error(self):
        self.shop_database.request.side_effect = requests.ConnectionError
        with self.assertRaisesRegex(ConnectionError, "^Can't get orders from database$"):
            self.shop_database.order_get()

    def test_order_get_connection_error(self):
        self.shop_database.request.side_effect = requests.ConnectionError
        with self.assertRaisesRegex(ConnectionError, "^Can't get order from database$"):
            self.shop_database.order_get(0)

    def test_orders_get_mock_check(self):
        self.shop_database.order_get()
        self.shop_database.request.assert_called_once_with('get', self.api_url + '/orders/')

    def test_order_get_mock_check(self):
        id_order = 0
        self.shop_database.order_get(id_order)
        self.shop_database.request.assert_called_once_with('get', self.api_url + '/orders/' + str(id_order))

    def test_order_delete(self):
        id_order = 0
        order = {
            **self.database['orders'][id_order],
            'ids_items': self.get_ids_items(id_order)
        }
        self.assertDictEqual(self.shop_database.order_delete(order['id']), order)

    def test_order_delete_wrong_type(self):
        with self.assertRaisesRegex(TypeError, "^Order ID must be an integer$"):
            self.shop_database.order_delete(MagicMock(spec=str))

    def test_order_delete_missing(self):
        with self.assertRaisesRegex(LookupError, "^Order with such ID doesn't exist$"):
            self.shop_database.order_delete(999)

    def test_order_delete_connection_error(self):
        self.shop_database.request.side_effect = requests.ConnectionError
        with self.assertRaisesRegex(ConnectionError, "^Can't delete order from database$"):
            self.shop_database.order_delete(0)

    def test_order_delete_mock_check(self):
        id_order = 0
        self.shop_database.order_delete(id_order)
        self.shop_database.request.assert_called_once_with('delete', self.api_url + '/orders/' + str(id_order))

    def test_order_put(self):
        order_updated = {
            'id': 1,
            'id_client': 1,
            'ids_items': [1, 2]
        }
        self.assertDictEqual(self.shop_database.order_put_patch(*order_updated.values()), order_updated)

    def test_order_put_wrong_type_id_client(self):
        with self.assertRaisesRegex(TypeError, "^Both order and client IDs must be integers$"):
            self.shop_database.order_put_patch(1, MagicMock(spec=str), [1, 2])

    def test_order_put_wrong_type_list(self):
        with self.assertRaisesRegex(TypeError, "^Items IDs must be a list$"):
            self.shop_database.order_put_patch(1, 1, MagicMock(spec=int))

    def test_order_put_items_empty(self):
        with self.assertRaisesRegex(ValueError, "^Items IDs must not be empty$"):
            self.shop_database.order_put_patch(1, 1, [])

    def test_order_put_wrong_type_items(self):
        with self.assertRaisesRegex(TypeError, "^Items IDs must all be integers$"):
            self.shop_database.order_put_patch(1, 1, [1, MagicMock(spec=str)])

    def test_item_put_missing_order(self):
        with self.assertRaisesRegex(LookupError, "^Referenced entities don't exist$"):
            self.shop_database.order_put_patch(999, 1, [1, 2])

    def test_item_put_missing_client(self):
        with self.assertRaisesRegex(LookupError, "^Referenced entities don't exist$"):
            self.shop_database.order_put_patch(1, 999, [1, 2])

    def test_item_put_missing_item(self):
        with self.assertRaisesRegex(LookupError, "^Referenced entities don't exist$"):
            self.shop_database.order_put_patch(1, 1, [1, 999])

    def test_order_put_connection_error(self):
        self.shop_database.request.side_effect = requests.ConnectionError
        with self.assertRaisesRegex(ConnectionError, "^Can't put order in database$"):
            self.shop_database.order_put_patch(1, 1, [1, 2])

    def test_order_put_mock_check(self):
        order_updated_id = 1
        order_updated = {
            'id_client': 1,
            'ids_items': [1, 2]
        }
        self.shop_database.order_put_patch(order_updated_id, **order_updated)
        self.shop_database.request.assert_called_once_with('put', self.api_url + '/orders/' + str(order_updated_id), data=order_updated)

    def test_order_patch(self):
        order = self.database['orders'][0]
        order_updated = {
            'id': order['id'],
            'id_client': 1,
            'ids_items': self.get_ids_items(order['id'])
        }
        self.assertDictEqual(self.shop_database.order_put_patch(order_updated['id'], id_client=order_updated['id_client']), order_updated)

    def test_order_patch_mock_check(self):
        order_updated_id = 1
        order_updated = {
            'id_client': 1
        }
        self.shop_database.order_put_patch(order_updated_id, id_client=order_updated['id_client'])
        self.shop_database.request.assert_called_once_with('patch', self.api_url + '/orders/' + str(order_updated_id), data=order_updated)

    def test_order_patch_no_arguments(self):
        with self.assertRaisesRegex(AttributeError, "^Patch must have at least one attribute$"):
            self.shop_database.order_put_patch(1)

    def test_order_patch_connection_error(self):
        self.shop_database.request.side_effect = requests.ConnectionError
        with self.assertRaisesRegex(ConnectionError, "^Can't patch order in database$"):
            self.shop_database.order_put_patch(1, id_client=0)

    def test_item_patch_missing_client(self):
        with self.assertRaisesRegex(LookupError, "^Referenced entities don't exist$"):
            self.shop_database.order_put_patch(1, id_client=999)

    def test_item_patch_missing_item(self):
        with self.assertRaisesRegex(LookupError, "^Referenced entities don't exist$"):
            self.shop_database.order_put_patch(1, ids_items=[1, 999])

    def tearDown(self):
        self.shop_database = None
        self.api_url = None
        self.get_new_id = None
        self.shop_database = None
        self.get_ids_items = None


class TestResponse:
    def __init__(self, value, status_code):
        self.value = value
        self.status_code = status_code

    def json(self):
        return self.value


if __name__ == '__main__':
    unittest.main()
