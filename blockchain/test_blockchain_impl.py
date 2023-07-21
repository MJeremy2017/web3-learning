import random
import time
from unittest import TestCase
from typing import List
from blockchain_impl import Block, Transaction, Wallet, verify
import secrets
from exceptions import *


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
        signed_txn = generate_signed_transaction(fr, to)
        results.append(signed_txn)
    return results


def generate_signed_transaction(wa: Wallet, wb: Wallet, amount: int = 0, ts=None) -> Transaction:
    unsigned_txn = Transaction(
        from_addr=wa.public_key,
        to_addr=wb.public_key,
        amount=random.randint(1, 10000) if amount == 0 else amount,
        ts=time.time() if ts is None else ts
    )
    signed_txn = wa.sign(unsigned_txn)
    return signed_txn


class TestWallet(TestCase):
    def setUp(self) -> None:
        self.wallet_a = Wallet()
        self.wallet_b = Wallet()

    def test_verify_legit_transaction(self):
        txn = generate_signed_transaction(self.wallet_a, self.wallet_b)
        got = verify(self.wallet_a.public_key, txn)
        self.assertEqual(got, True)

    def test_verify_illegal_transaction(self):
        txn = generate_signed_transaction(self.wallet_a, self.wallet_b)
        txn.signature = b'123'
        got = verify(self.wallet_a.public_key, txn)
        self.assertEqual(got, False)


class TestBlock(TestCase):
    prev_hash = generate_random_hash()
    wa = Wallet()
    wb = Wallet()
    wc = Wallet()
    reward = 10
    difficulty = 2

    def setUp(self) -> None:
        self.prev_block = Block(
            prev_block=None,
            transactions=[
                generate_signed_transaction(self.wc, self.wa, 100)
            ],
            reward=self.reward,
            difficulty=self.difficulty
        )
        self.block = Block(
            prev_block=self.prev_block,
            transactions=[
                generate_signed_transaction(self.wa, self.wb, 80)
            ],
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
        signed_txn = generate_signed_transaction(self.wa, self.wb)
        self.block.verify_signature(signed_txn)

    def test_verify_false_signed_transaction(self):
        txn = generate_signed_transaction(self.wa, self.wb)
        txn.signature = b'123'
        with self.assertRaises(InvalidSignatureException):
            self.block.verify_signature(txn)

    def test_verify_insufficient_funds(self):
        signed_txn = generate_signed_transaction(self.wa, self.wb)
        prev_block = Block(
            prev_block=None,
            transactions=[],
            reward=self.reward,
            difficulty=self.difficulty
        )
        block = Block(
            prev_block=prev_block,
            transactions=[
                signed_txn
            ],
            reward=self.reward,
            difficulty=self.difficulty
        )

        with self.assertRaises(InsufficientFundsException):
            block.verify_sufficient_funds(signed_txn)

    def test_verify_sufficient_funds(self):
        txn1 = generate_signed_transaction(self.wc, self.wa, 30)
        txn2 = generate_signed_transaction(self.wa, self.wb, 10)
        prev_block = Block(
            prev_block=None,
            transactions=[txn1],
            reward=self.reward,
            difficulty=self.difficulty
        )
        block = Block(
            prev_block=prev_block,
            transactions=[
                txn2
            ],
            reward=self.reward,
            difficulty=self.difficulty
        )

        block.verify_sufficient_funds(txn2)

    def test_verify_sufficient_funds_in_the_same_block(self):
        txn1 = generate_signed_transaction(self.wc, self.wa, 30, ts=1)
        txn2 = generate_signed_transaction(self.wa, self.wb, 10, ts=2)
        prev_block = Block(
            prev_block=None,
            transactions=[],
            reward=self.reward,
            difficulty=self.difficulty
        )
        block = Block(
            prev_block=prev_block,
            transactions=[
                txn1,
                txn2
            ],
            reward=self.reward,
            difficulty=self.difficulty
        )

        block.verify_sufficient_funds(txn2)

    def test_verify_another_block_with_wrong_transaction_fields(self):
        other = Block(
            prev_block=self.prev_block,
            transactions=[
                generate_signed_transaction(self.wa, self.wb, 70)
            ],
            reward=self.reward,
            difficulty=self.difficulty
        )
        with self.assertRaises(ValueError):
            self.block.verify_another_block(other)

    def test_verify_another_block_with_correct_transaction_fields(self):
        other = Block(
            prev_block=self.prev_block,
            transactions=[
                generate_signed_transaction(self.wa, self.wb, 80)
            ],
            reward=self.reward,
            difficulty=self.difficulty
        )
        other.mine(self.miner.public_key)
        self.block.verify_another_block(other)

    def test_verify_wrong_block_hash(self):
        other = Block(
            prev_block=self.prev_block,
            transactions=[
                generate_signed_transaction(self.wa, self.wb, 80)
            ],
            reward=self.reward,
            difficulty=self.difficulty
        )
        with self.assertRaises(ValueError):
            self.block.verify_block_hash(other)

    def test_verify_correct_block_hash(self):
        other = Block(
            prev_block=self.prev_block,
            transactions=[
                generate_signed_transaction(self.wa, self.wb, 80)
            ],
            reward=self.reward,
            difficulty=self.difficulty
        )
        other_miner = Wallet()
        other.mine(other_miner.public_key)
        self.block.verify_block_hash(other)

    def test_verify_other_block(self):
        other = Block(
            prev_block=self.prev_block,
            transactions=[
                generate_signed_transaction(self.wa, self.wb, 80)
            ],
            reward=self.reward,
            difficulty=self.difficulty
        )
        other_miner = Wallet()
        other.mine(other_miner.public_key)
        self.block.verify_another_block(other)



