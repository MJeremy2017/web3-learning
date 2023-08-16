import requests


def add_transaction(host: str, port: int, sender: str, receiver: str, signature: str, amount: int):
    data = {
        "sender": sender,
        "receiver": receiver,
        "signature": signature,
        "amount": amount
    }
    url = host + ":" + str(port) + "/transaction/new"
    resp: requests.Response = requests.post(url, json=data)
    if resp.status_code == 200:
        print("Successfully added transaction")
    else:
        raise Exception(f"Error adding transaction {resp.text}")
