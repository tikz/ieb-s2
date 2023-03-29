# IEB (S2)

## Run

### Local
```
pip install pipenv
pipenv install
pipenv shell

ENCRYPTION_KEY=<key> python server.py <port> <API base URL>
```

### Ejemplo instancia Docker

```
docker run --add-host=host.docker.internal:host-gateway -p 1234:1234 --env ENCRYPTION_KEY=oHFJ7Llz1EI6MP478jrhHLJJFOmnvvHxoGOPxVR7oUM= ghcr.io/tikz/ieb-s2:main 1234 http://host.docker.internal:9090/api
```