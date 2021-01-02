import unittest
from src.shop.shop_database import ShopDatabase


class TestShopDatabase(unittest.TestCase):
    def test_init(self):
        shop_database = ShopDatabase('http://example.com')
        self.assertIsInstance(shop_database, ShopDatabase)


if __name__ == '__main__':
    unittest.main()
