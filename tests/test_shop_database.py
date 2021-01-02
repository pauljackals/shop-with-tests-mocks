import unittest
from src.shop.shop_database import ShopDatabase


class TestShopDatabase(unittest.TestCase):
    def test_init(self):
        shop_database = ShopDatabase('http://example.com')
        self.assertIsInstance(shop_database, ShopDatabase)

    def test_init_wrong_type(self):
        with self.assertRaisesRegex(TypeError, "^Api URL must be a valid url string$"):
            ShopDatabase(545)


if __name__ == '__main__':
    unittest.main()
