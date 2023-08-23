import requests
import base64


def add_transaction(host: str, port: int, sender: str, receiver: str, signature: bytes, amount: int):
    data = {
        "sender": sender,
        "receiver": receiver,
        "signature": base64.b64encode(signature).decode('utf-8'),
        "amount": amount
    }
    url = host + ":" + str(port) + "/transaction/new"
    resp: requests.Response = requests.post(url, json=data)
    if resp.status_code == 200:
        print("Successfully added transaction")
    else:
        print(f"Error adding transaction {resp.text}")
        raise Exception(f"Error adding transaction {resp.text}")


def mine_block(host: str, port: int, miner: str):
    data = {
        "miner_addr": miner
    }
    url = host + ":" + str(port) + "/blockchain/mine"
    resp: requests.Response = requests.get(url, json=data)
    if resp.status_code == 200:
        print(f"Successfully mined transaction {resp.text}")
    else:
        raise Exception(f"Error mining transaction {resp.text}")

