import unittest
from unittest.mock import Mock
from src.shop.shop_app import ShopApp


class TestShopApp(unittest.TestCase):
    def setUp(self):
        mock_shop_database = Mock()
        mock_shop_database.client_post.return_value = {'id': 2}

        self.shop_app = ShopApp('http://example.com')
        self.shop_app.shop_database = mock_shop_database

    def test_register_client(self):
        self.assertEqual(self.shop_app.register_client('Henry', 'Glenn', 'henry_glenn@example.com'), 2)

    def test_register_client_mock_check(self):
        params = 'Henry', 'Glenn', 'henry_glenn@example.com'
        self.shop_app.register_client(*params)
        self.shop_app.shop_database.client_post.assert_called_with(*params)

    def tearDown(self):
        self.shop_app = None


if __name__ == '__main__':
    unittest.main()
