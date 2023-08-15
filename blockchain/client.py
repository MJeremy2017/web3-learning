from utils import unpickle_wallets, unpickle_accounts, generate_signed_transaction
import random
import requests

HOST = 'http://localhost'
PORT = 5000


def add_transaction(sender: str, receiver: str, signature: str, amount: int):
    data = {
        "sender": sender,
        "receiver": receiver,
        "signature": signature,
        "amount": amount
    }
    url = HOST + ":" + str(PORT) + "/transaction/new"
    resp: requests.Response = requests.post(url, json=data)
    if resp.status_code == 200:
        print("Successfully added transaction")
    else:
        raise Exception(f"Error adding transaction {resp.text}")


if __name__ == '__main__':
    accounts = unpickle_accounts('tmp/accounts')
    wallets = unpickle_wallets('tmp/wallets')

    wa = wallets[0]
    wb = wallets[1]
    amount = random.randint(1, accounts[0])
    txn = generate_signed_transaction(wa, wb, amount)
    add_transaction(sender=str(txn.from_addr),
                    receiver=str(txn.to_addr),
                    signature=str(txn.signature),
                    amount=txn.amount)
