import logging
import sys

from twisted.internet import protocol, reactor, task
from storage import ProductStorage


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClientSession:
    """ Representa una sesión activa y contiene
    el objeto cliente y el código de producto solicitado. """

    def __init__(self, client, product_code: str):
        self.client = client
        self.product_code = product_code
        STORAGE.put(self.product_code)

    def __eq__(self, client):
        return self.client == client


class ServerProtocol(protocol.Protocol):
    def connectionMade(self):
        self._peer = self.transport.getPeer()
        logging.info(f"New connection from {self._peer}")

    def connectionLost(self, client):
        logging.info(f"Closed connection from {self._peer}")
        self.factory.clientConnectionLost(self)

    def dataReceived(self, product_code: bytes):
        self.factory.clientRequestProduct(self, product_code)


class ServerFactory(protocol.Factory):
    protocol = ServerProtocol

    def __init__(self):
        self.clients = []
        self.lc = task.LoopingCall(self.tick)
        self.lc.start(1)

    def tick(self):
        for client_session in self.clients:
            product = STORAGE.get(client_session.product_code)
            if product.error:
                logger.error(
                    f"Closing client connection, Product error: {product.error}")
                client_session.client.transport.loseConnection()
            elif not product.pending:
                client_session.client.transport.write(product.serialize())

    def clientRequestProduct(self, client, product_code: bytes):
        self.clients.append(ClientSession(
            client, product_code.decode("utf-8")))

    def clientConnectionLost(self, client):
        self.clients.remove(client)
        self.clear()

    def clear(self):
        """ Elimina del storage aquellos productos que no tengan
        al menos 1 cliente requiriéndolos actualmente. """
        for product_code in set(STORAGE.all) - set(c.product_code for c in self.clients):
            STORAGE.delete(product_code)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: server.py <port> <base API URL>")
        sys.exit(1)

    port = int(sys.argv[1])
    api_url = sys.argv[2]
    STORAGE = ProductStorage(api_url)

    factory = ServerFactory()
    reactor.listenTCP(port, factory)
    reactor.run()
