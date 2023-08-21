import requests
import base64


def add_transaction(host: str, port: int, sender: str, receiver: str, signature: bytes, amount: int):
    print('adding transaction, type', type(signature))
    # TODO fix error using base64
    data = {
        "sender": sender,
        "receiver": receiver,
        "signature": signature.decode('utf-8'),
        "amount": amount
    }
    url = host + ":" + str(port) + "/transaction/new"
    resp: requests.Response = requests.post(url, json=data)
    if resp.status_code == 200:
        print("Successfully added transaction")
    else:
        print(f"Error adding transaction {resp.text}")
        raise Exception(f"Error adding transaction {resp.text}")
