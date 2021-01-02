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
            ]
        }

        def request_custom(method, url):
            url_split = url.split('/')
            endpoint = url_split[-2]
            id_param = int(url_split[-1])
            if method == 'get':
                for entity in self.database[endpoint]:
                    if entity['id'] == id_param:
                        return TestResponse(entity, 200)
                return TestResponse({}, 404)
        self.api_url = 'http://example.com'
        self.shop_database = ShopDatabase(self.api_url)
        self.shop_database.request = Mock()
        self.shop_database.request.side_effect = request_custom

    def test_init(self):
        self.assertIsInstance(self.shop_database, ShopDatabase)

    def test_init_wrong_type(self):
        with self.assertRaisesRegex(TypeError, "^Api URL must be a valid url string$"):
            ShopDatabase(545)

    def test_init_invalid(self):
        with self.assertRaisesRegex(TypeError, "^Api URL must be a valid url string$"):
            ShopDatabase('http://examplecom')

    def test_client_get(self):
        id_client = 1
        self.assertDictEqual(self.shop_database.client_get(id_client), self.database['clients'][id_client])

    def test_client_get_wrong_type(self):
        with self.assertRaisesRegex(TypeError, "^Client ID must an integer$"):
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

    def tearDown(self):
        self.shop_database = None


class TestResponse:
    def __init__(self, value, status_code):
        self.value = value
        self.status_code = status_code

    def json(self):
        return self.value


if __name__ == '__main__':
    unittest.main()
