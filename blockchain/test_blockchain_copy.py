import hashlib
import random
from unittest import TestCase
from typing import List
from blockchain.blockchain_copy import Block, Transaction, Wallet
import secrets
from blockchain.utils import verify


def generate_random_hash():
    return secrets.token_hex(20)


def generate_random_transactions(n_users: int, n_txn: int):
    wallets: List[Wallet] = []
    for _ in range(n_users):
        w = Wallet()
        wallets.append(w)
    results = []
    for i in range(n_txn):
        i = j = 0
        while i != j:
            i, j = random.randint(0, n_users - 1), random.randint(0, n_users - 1)
        fr = wallets[i]
        to = wallets[j]
        signed_txn = generate_random_signed_transaction(fr, to)
        results.append(signed_txn)
    return results


def generate_random_signed_transaction(wa: Wallet, wb: Wallet):
    unsigned_txn = Transaction(
        from_addr=wa.public_key_str,
        to_addr=wb.public_key_str,
        amount=random.randint(1, 10000),
    )
    signed_txn = wa.sign(unsigned_txn)
    return signed_txn


class TestWallet(TestCase):
    def setUp(self) -> None:
        self.wallet_a = Wallet()
        self.wallet_b = Wallet()

    def test_verify_legit_transaction(self):
        txn = generate_random_signed_transaction(self.wallet_a, self.wallet_b)
        got = verify(self.wallet_a.public_key, txn)
        self.assertEqual(got, True)

    def test_verify_illegal_transaction(self):
        txn = generate_random_signed_transaction(self.wallet_a, self.wallet_b)
        txn.signature = hashlib.sha256("abc".encode()).hexdigest()
        got = verify(self.wallet_a.public_key, txn)
        self.assertEqual(got, False)


class TestBlock(TestCase):
    prev_hash = generate_random_hash()
    txns = generate_random_transactions(3, 10)
    reward = 10
    difficulty = 1

    def setUp(self) -> None:
        self.block = Block(
            prev_hash=self.prev_hash,
            transactions=self.txns,
            reward=self.reward,
            difficulty=self.difficulty
        )
        self.miner = Wallet()

    def test_mine(self):
        self.block.mine(
            miner_addr=self.miner.public_key_str
        )

        self.assertEqual(self.block.block_hash[:self.difficulty], "0" * self.difficulty)
