import requests
import time
import logging
import threading

from product import ProductEncrypted as Product

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductStorage:
    """
    Base de datos en memoria que mantiene productos únicos y obtiene
    actualizaciones periódicas de los precios via threads.
    """

    def __init__(self, api_url):
        self._api_url = api_url
        self._products = {}
        threading.Thread(target=self._run).start()

    def _run(self):
        while True:
            for product_code in self._products.keys():
                threading.Thread(target=self._fetch,
                                 args=(product_code,)).start()
            time.sleep(1)

    def _fetch(self, product_code: str):
        try:
            raw = requests.get(
                f'{self._api_url}/products/{product_code}').content
        except Exception as e:
            self._set_error(product_code, e)
        else:
            self._update(product_code, raw)

    def _update(self, product_code: str, raw: bytes):
        self._products[product_code].from_json(raw)

    def _set_error(self, product_code: str, error):
        self._products[product_code].error = error

    def put(self, product_code: str):
        self._products[product_code] = Product()

    def get(self, product_code: str) -> Product:
        return self._products[product_code]

    def delete(self, product_code: str) -> Product:
        del self._products[product_code]

    @property
    def all(self) -> list:
        return self._products.keys()
