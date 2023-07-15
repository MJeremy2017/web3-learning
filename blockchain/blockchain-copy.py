import logging
import time
from typing import List
from dataclasses import dataclass
import hashlib


@dataclass
class Transaction:
    from_addr: str
    to_addr: str
    amount: int
    signature: str

    def __str__(self):
        return self.from_addr + self.to_addr + str(self.amount) + self.signature


class Block:
    def __init__(self, transactions: List[Transaction], reward: int, difficulty: int):
        self.transactions = transactions
        self.reward = reward
        self.difficulty = difficulty
        self.nonce = 0

    def mine(self, miner_addr: str):
        start_time = time.time()
        coinbase_transaction = self._generate_coinbase_transaction(self.reward, miner_addr)
        self.verify_transactions(self.transactions)
        while 1:
            block_hash = self._hash(
                self.transactions,
                coinbase_transaction,
                self.nonce
            )
            if self._valid_block_hash(block_hash):
                time_cost = time.time() - start_time
                logging.info(f"Block mined time cost {time_cost}")
                break
            else:
                self.nonce += 1

    def _generate_coinbase_transaction(self, reward: int, miner_addr: str) -> Transaction:
        # TODO generate signature
        return Transaction(
            from_addr="",
            to_addr=miner_addr,
            amount=reward,
            signature=""
        )

    def _hash(self, transactions: List[Transaction], coinbase_transaction: Transaction, nonce: int) -> str:
        encode_str = ""
        for txn in transactions + [coinbase_transaction]:
            encode_str += str(txn)
        encode_str += str(nonce)
        return hashlib.sha256(encode_str).hexdigest()

    def _valid_block_hash(self, block_hash: str):
        return block_hash[:self.difficulty] == "0" * self.difficulty

    def verify_transactions(self, transactions: List[Transaction]):
        pass
