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
