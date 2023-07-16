import hashlib
import random
from unittest import TestCase
from blockchain.blockchain_copy import Block, Transaction, Wallet
import secrets
from blockchain.utils import verify


def generate_random_hash():
    return secrets.token_hex(20)


def generate_random_key_pair():
    pass


def generate_random_transactions(num: int):
    results = []
    for i in range(num):
        generate_random_key_pair()
        txn = Transaction(
            from_addr="",
            to_addr="",
            amount=random.randint(1, 10000),
            signature=""
        )


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
    txns = generate_random_transactions(5)
    reward = 10
    difficulty = 1

    def setUp(self) -> None:
        self.block = Block(
            prev_hash=self.prev_hash,
            transactions=self.txns,
            reward=self.reward,
            difficulty=self.difficulty
        )

    def test_mine(self):
        self.fail()
