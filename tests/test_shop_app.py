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
        mock_shop_database.client_delete.return_value = {}
        mock_shop_database.client_put_patch.return_value = {}

        mock_shop_database.item_post.return_value = {'id': 3}
        mock_shop_database.item_get.side_effect = lambda id_item=None: get_side_effect('items', id_item)
        mock_shop_database.item_delete.return_value = {}
        mock_shop_database.item_put_patch.return_value = {}

        mock_shop_database.order_post.return_value = {'id': 2}
        mock_shop_database.order_get.side_effect = lambda id_order=None: get_side_effect('orders', id_order)
        mock_shop_database.order_delete.return_value = {}

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

    def test_download_client_mock_check(self):
        id_client = 0
        self.shop_app.download_client(id_client)
        self.shop_app.shop_database.client_get.assert_called_with(id_client)

    def test_download_all_clients(self):
        clients = self.database_simplified['clients']
        self.assertListEqual(self.shop_app.download_all_clients(), clients)

    def test_download_all_clients_mock_check(self):
        self.shop_app.download_all_clients()
        self.shop_app.shop_database.client_get.assert_called_with()

    def test_remove_client(self):
        self.assertTrue(self.shop_app.remove_client(1))

    def test_remove_client_mock_check(self):
        id_client = 0
        self.shop_app.remove_client(id_client)
        self.shop_app.shop_database.client_delete.assert_called_with(id_client)

    def test_modify_client(self):
        self.assertTrue(self.shop_app.modify_client(1, 'Henry', 'Glenn', 'henry_glenn@example.com'))

    def test_modify_client_mock_check(self):
        id_client = 0
        name_first = 'Henry'
        email = 'henry_glenn@example.com'
        self.shop_app.modify_client(id_client, name_first=name_first, email=email)
        self.shop_app.shop_database.client_put_patch.assert_called_with(id_client, name_first, None, email)

    def test_add_item(self):
        self.assertEqual(self.shop_app.add_item('PlayStation 5', 2199.99), 3)

    def test_add_item_mock_check(self):
        params = 'PlayStation 5', 2199.99
        self.shop_app.add_item(*params)
        self.shop_app.shop_database.item_post.assert_called_with(*params)

    def test_download_item(self):
        item = self.database_simplified['items'][1]
        self.assertDictEqual(self.shop_app.download_item(item['id']), item)

    def test_download_item_mock_check(self):
        id_item = 0
        self.shop_app.download_item(id_item)
        self.shop_app.shop_database.item_get.assert_called_with(id_item)

    def test_download_all_items(self):
        items = self.database_simplified['items']
        self.assertListEqual(self.shop_app.download_all_items(), items)

    def test_download_all_items_mock_check(self):
        self.shop_app.download_all_items()
        self.shop_app.shop_database.item_get.assert_called_with()

    def test_remove_item(self):
        self.assertTrue(self.shop_app.remove_item(1))

    def test_remove_item_mock_check(self):
        id_item = 0
        self.shop_app.remove_item(id_item)
        self.shop_app.shop_database.item_delete.assert_called_with(id_item)

    def test_modify_item(self):
        self.assertTrue(self.shop_app.modify_item(1, value=799.99))

    def test_modify_item_mock_check(self):
        params = 0, 'PlayStation 5', 2199.99
        self.shop_app.modify_item(*params)
        self.shop_app.shop_database.item_put_patch.assert_called_with(*params)

    def test_make_order(self):
        self.assertEqual(self.shop_app.make_order(0, [0]), 2)

    def test_make_order_mock_check(self):
        params = 0, [0]
        self.shop_app.make_order(*params)
        self.shop_app.shop_database.order_post.assert_called_with(*params)

    def test_download_order(self):
        order = self.database_simplified['orders'][1]
        self.assertDictEqual(self.shop_app.download_order(order['id']), order)

    def test_download_order_mock_check(self):
        id_order = 0
        self.shop_app.download_order(id_order)
        self.shop_app.shop_database.order_get.assert_called_with(id_order)

    def test_download_all_orders(self):
        orders = self.database_simplified['orders']
        self.assertListEqual(self.shop_app.download_all_orders(), orders)

    def test_download_all_orders_mock_check(self):
        self.shop_app.download_all_orders()
        self.shop_app.shop_database.order_get.assert_called_with()

    def test_remove_order(self):
        self.assertTrue(self.shop_app.remove_order(1))

    def test_remove_order_mock_check(self):
        id_order = 0
        self.shop_app.remove_order(id_order)
        self.shop_app.shop_database.order_delete.assert_called_with(id_order)

    def tearDown(self):
        self.shop_app = None
        self.database_simplified = None


if __name__ == '__main__':
    unittest.main()
