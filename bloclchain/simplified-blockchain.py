import hashlib
import time
from datetime import datetime
import json


class Transaction:
	def __init__(self, sender, receiver, amount):
		self.sender = sender
		self.receiver = receiver
		self.amount = amount


class Block:
	def __init__(self, transactions, time, previous_hash=''):
		self.transactions = transactions
		self.time = time
		self.previous_hash = previous_hash
		self.hash = self.calculate_hash()

	def calculate_hash(self):
		hash_transactions = ""
		for transaction in self.transactions:
			hash_transactions += transaction.sender + transaction.receiver + str(transaction.amount)

		hash_string = str(self.time) + hash_transactions + self.previous_hash
		hash_encoded = json.dumps(hash_string, sort_keys=True).encode()
		return hashlib.sha256(hash_encoded).hexdigest()


class Blockchain:
	def __init__(self):
		self.chain = [self.create_genesis_block()]

	def create_genesis_block(self):
		transactions = [Transaction("Genesis sender", "Genesis receiver", 0)]
		time = datetime.now()
		return Block(transactions, time, "0")

	def get_latest_block(self):
		return self.chain[-1]

	def add_block(self, transactions):
		time = datetime.now()
		new_block = Block(transactions, time, self.get_latest_block().hash)
		self.chain.append(new_block)


if __name__ == '__main__':
	my_coin = Blockchain()

	transaction1 = Transaction("Alice", "Bob", 50)
	transaction2 = Transaction("Bob", "Alice", 25)

	my_coin.add_block([transaction1, transaction2])
	print(my_coin.get_latest_block().transactions)
