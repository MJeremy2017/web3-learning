from flask import Flask, request
from blockchain_impl import BlockChain, Transaction, Wallet, PublicKey, PrivateKey
from cryptography.hazmat.primitives import serialization
from utils import generate_blockchain
from typing import List
import pickle

app = Flask(__name__)


def deserialize_public_key(data: str) -> PublicKey:
    return PublicKey(serialization.load_pem_public_key(data.encode('utf-8')))


def deserialize_private_key(data: str) -> PrivateKey:
    return PrivateKey(serialization.load_pem_private_key(data.encode('utf-8'), password=None))


# TODO: init new blockchain
blockchain, accounts, wallets = generate_blockchain(3, 5, 3, reward=10, difficulty=1)


def pickle_wallets(wallets: List[Wallet]):
    wallets_serial = []
    for w in wallets:
        wallets_serial.append((str(w.public_key), str(w.private_key)))
    with open('wallets', 'wb') as f:
        pickle.dump(wallets_serial, f)


def unpickle_wallets(file: str) -> List[Wallet]:
    with open(file, 'rb') as f:
        wallets_serial = pickle.load(f)
    wallets = []
    for w in wallets_serial:
        wd = Wallet(public_key=deserialize_public_key(w[0]), private_key=deserialize_private_key(w[1]))
        wallets.append(wd)
    return wallets


def save_accounts_and_wallets(accounts: List[int], wallets: List[Wallet]):
    with open('accounts', 'wb') as f:
        pickle.dump(accounts, f)

    pickle_wallets(wallets)


save_accounts_and_wallets(accounts, wallets)


@app.route('/transaction/new', methods=['POST'])
def add_transaction():
    data = request.get_json()
    sender: str = str(data['sender'])
    receiver: str = str(data['receiver'])
    amount: int = int(data['amount'])
    signature: bytes = bytes(data['signature'])
    txn = Transaction(
        deserialize_public_key(sender),
        deserialize_public_key(receiver),
        amount,
        signature
    )

    # TODO Add to blockchain


if __name__ == '__main__':
    w = Wallet()
    serial = str(w.public_key)
    print('original', type(w.public_key), w.public_key)
    deserial_obj = PublicKey(serialization.load_pem_public_key(serial.encode('utf-8')))

    print(type(deserial_obj))
    print(deserial_obj)

    assert w.public_key == deserial_obj
