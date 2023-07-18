import random
from unittest import TestCase
from typing import List
from blockchain_copy import Block, Transaction, Wallet, verify
import secrets
from exceptions import InvalidSignatureException


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
        from_addr=wa.public_key,
        to_addr=wb.public_key,
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
        txn.signature = b'123'
        got = verify(self.wallet_a.public_key, txn)
        self.assertEqual(got, False)


class TestBlock(TestCase):
    prev_hash = generate_random_hash()
    txns = generate_random_transactions(n_users=3, n_txn=10)
    reward = 10
    difficulty = 2

    def setUp(self) -> None:
        prev_block = Block(
            prev_block=None,
            transactions=[],
            reward=self.reward,
            difficulty=self.difficulty
        )
        self.block = Block(
            prev_block=prev_block,
            transactions=self.txns,
            reward=self.reward,
            difficulty=self.difficulty
        )
        self.miner = Wallet()

    def test_mine(self):
        self.block.mine(
            miner_addr=self.miner.public_key
        )

        self.assertEqual(self.block.block_hash[:self.difficulty], "0" * self.difficulty)

    def test_verify_signed_transaction(self):
        wa = Wallet()
        wb = Wallet()
        signed_txn = generate_random_signed_transaction(wa, wb)
        self.block.verify_single_transaction(signed_txn)

    def test_verify_false_signed_transaction(self):
        wa = Wallet()
        wb = Wallet()
        txn = generate_random_signed_transaction(wa, wb)
        txn.signature = b'123'
        with self.assertRaises(InvalidSignatureException):
            self.block.verify_single_transaction(txn)
