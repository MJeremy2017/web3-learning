import hashlib
from datetime import datetime
import json
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import binascii
from typing import List


class Transaction:
    def __init__(self, sender, receiver, amount, signature=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.signature = signature

    def to_dict(self):
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'signature': self.signature
        }


class Block:
    def __init__(self, transactions: List[Transaction], time, previous_hash=''):
        self.transactions = transactions
        self.time = time
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        hash_transactions = ""
        for transaction in self.transactions:
            hash_transactions += str(transaction.sender) + str(transaction.receiver) + str(transaction.amount)

        hash_string = str(self.time) + hash_transactions + self.previous_hash + str(self.nonce)
        hash_encoded = json.dumps(hash_string, sort_keys=True).encode()
        return hashlib.sha256(hash_encoded).hexdigest()

    def mine_block(self, difficulty):
        while self.hash[:difficulty] != "0" * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()


class Blockchain:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.reward = 100

    def create_genesis_block(self):
        transactions = [Transaction("Genesis sender", "Genesis receiver", 0, "")]
        time = datetime.now()
        return Block(transactions, time, "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_transactions(self, transactions: List[Transaction]):
        self.pending_transactions.extend(transactions)

    def add_block(self, miner_address):
        time = datetime.now()
        new_block = Block(self.pending_transactions, time, self.get_latest_block().hash)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self.pending_transactions = [Transaction(None, miner_address, self.reward, "")]


class Wallet:
    def __init__(self):
        key_pair = RSA.generate(2048)
        self.private_key = key_pair.export_key()
        self.public_key = key_pair.publickey().export_key()

    def sign_transaction(self, transaction):
        priv_key_obj = RSA.import_key(self.private_key)
        message = SHA256.new(str(transaction.to_dict()).encode('utf8'))
        signature = pkcs1_15.new(priv_key_obj).sign(message)
        return binascii.hexlify(signature).decode('ascii')


if __name__ == '__main__':
    alice_wallet = Wallet()
    bob_wallet = Wallet()
    transaction = Transaction(alice_wallet.public_key, bob_wallet.public_key, 50)
    signature = alice_wallet.sign_transaction(transaction)
    transaction.signature = signature

    chain = Blockchain(2)
    chain.add_transactions([transaction])
    # Alice is also the miner
    chain.add_block(alice_wallet.public_key)

    for txn in chain.get_latest_block().transactions:
        print(txn.to_dict())
