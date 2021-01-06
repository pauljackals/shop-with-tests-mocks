from .shop_database import ShopDatabase


class ShopApp:
    def __init__(self, api_url):
        self.shop_database = ShopDatabase(api_url)

    def register_client(self, name_first, name_last, email):
        client = self.shop_database.client_post(name_first, name_last, email)
        return client['id']

    def download_client(self, id_client):
        client = self.shop_database.client_get(id_client)
        return client

    def download_all_clients(self):
        clients = self.shop_database.client_get()
        return clients

    def remove_client(self, id_client):
        self.shop_database.client_delete(id_client)
        return True

    def modify_client(self, id_client, name_first=None, name_last=None, email=None):
        self.shop_database.client_put_patch(id_client, name_first, name_last, email)
        return True

    def add_item(self, name, value):
        item = self.shop_database.item_post(name, value)
        return item['id']

    def download_item(self, id_item):
        item = self.shop_database.item_get(id_item)
        return item

    def download_all_items(self):
        items = self.shop_database.item_get()
        return items

    def remove_item(self, id_item):
        self.shop_database.item_delete(id_item)
        return True

    def modify_item(self, id_item, name=None, value=None):
        self.shop_database.item_put_patch(id_item, name, value)
        return True

    def make_order(self, id_client, ids_items):
        order = self.shop_database.order_post(id_client, ids_items)
        return order['id']

    def download_order(self, id_order):
        order = self.shop_database.order_get(id_order)
        return order
