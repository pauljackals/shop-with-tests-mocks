import unittest
from unittest.mock import Mock
from src.shop.shop_app import ShopApp


class TestShopApp(unittest.TestCase):
    def setUp(self):
        self.database_simplified = {
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
                    'id_client': 0,
                    'ids_items': [2]
                },
                {
                    'id': 1,
                    'id_client': 1,
                    'ids_items': [1, 0]
                }
            ]
        }

        def get_side_effect(endpoint, id_entity):
            if id_entity is None:
                return self.database_simplified[endpoint]
            else:
                return self.database_simplified[endpoint][id_entity]

        mock_shop_database = Mock()
        mock_shop_database.client_post.return_value = {'id': 2}
        mock_shop_database.client_get.side_effect = lambda id_client=None: get_side_effect('clients', id_client)

        self.shop_app = ShopApp('http://example.com')
        self.shop_app.shop_database = mock_shop_database

    def test_register_client(self):
        self.assertEqual(self.shop_app.register_client('Henry', 'Glenn', 'henry_glenn@example.com'), 2)

    def test_register_client_mock_check(self):
        params = 'Henry', 'Glenn', 'henry_glenn@example.com'
        self.shop_app.register_client(*params)
        self.shop_app.shop_database.client_post.assert_called_with(*params)

    def test_download_client(self):
        client = self.database_simplified['clients'][1]
        self.assertDictEqual(self.shop_app.download_client(client['id']), client)

    def tearDown(self):
        self.shop_app = None
        self.database_simplified = None


if __name__ == '__main__':
    unittest.main()
