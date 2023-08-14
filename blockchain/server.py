from flask import Flask, request
from blockchain_impl import BlockChain, Transaction, Wallet, PublicKey, PrivateKey
from utils import generate_blockchain, deserialize_public_key, save_accounts_and_wallets

app = Flask(__name__)



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

    blockchain.add_transaction(txn)


if __name__ == '__main__':
    blockchain, accounts, wallets = generate_blockchain(3, 5, 3, reward=10, difficulty=1)
    save_accounts_and_wallets(accounts, wallets)
