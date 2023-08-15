import random
from unittest import TestCase
from typing import List
from blockchain_impl import Block, Transaction, Wallet, verify, verify_transaction_has_sufficient_funds
import secrets
from exceptions import *
from utils import generate_signed_transaction, generate_blockchain


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
            verify_transaction_has_sufficient_funds(block, signed_txn)

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

        verify_transaction_has_sufficient_funds(block, txn2)

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

        verify_transaction_has_sufficient_funds(block, txn2)

    def test_verify_insufficient_funds_in_the_same_block(self):
        txn1 = generate_signed_transaction(self.wc, self.wa, 10, ts=1)
        txn2 = generate_signed_transaction(self.wa, self.wb, 30, ts=2)
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

        with self.assertRaises(InsufficientFundsException):
            verify_transaction_has_sufficient_funds(block, txn2)


class TestBlockChain(TestCase):
    wa = Wallet()
    wb = Wallet()
    wc = Wallet()
    wm = Wallet()
    reward = 10
    difficulty = 2

    def setUp(self) -> None:
        pass

    def test_mine_succeed_with_valid_block(self):
        blockchain, accounts, wallets = generate_blockchain(length=3, n_transactions=1, n_users=3)
        blockchain.add_transaction(generate_signed_transaction(
            wallets[0],
            wallets[1],
            amount=random.randint(1, accounts[0])
        ))
        last_block = blockchain.chain[-1]
        blockchain.mine(self.wm.public_key)
        new_last_block = blockchain.chain[-1]
        self.assertEqual(new_last_block.prev_block, last_block)
        self.assertEqual(last_block.next_block, new_last_block)

    def test_mine_fails_with_invalid_block(self):
        blockchain, accounts, wallets = generate_blockchain(length=3, n_transactions=1, n_users=3)
        txn = generate_signed_transaction(
            wallets[0],
            wallets[1],
            amount=random.randint(1, accounts[0])
        )
        txn.signature = b'0x0'

        blockchain.add_transaction(txn)
        last_block = blockchain.chain[-1]
        blockchain.mine(self.wm.public_key)
        new_last_block = blockchain.chain[-1]
        self.assertEqual(new_last_block, last_block)

    def test_verify_correct_block(self):
        blockchain, accounts, wallets = generate_blockchain(
            length=3,
            n_transactions=1,
            n_users=3,
            reward=self.reward,
            difficulty=self.difficulty
        )
        prev_block = blockchain.chain[-1]
        other = Block(
            prev_block=prev_block,
            transactions=[
                generate_signed_transaction(
                    wallets[0],
                    wallets[1],
                    amount=random.randint(1, accounts[0])
                )
            ],
            reward=self.reward,
            difficulty=self.difficulty
        )
        other.mine(self.wa.public_key)
        blockchain.verify_block(other)

    def test_verify_wrong_block(self):
        blockchain, accounts, wallets = generate_blockchain(
            length=3,
            n_transactions=1,
            n_users=3,
            reward=self.reward,
            difficulty=self.difficulty
        )
        invalid_txn = generate_signed_transaction(
            wallets[0],
            wallets[1],
            amount=random.randint(1, accounts[0])
        )
        invalid_txn.signature = b'0x0'
        prev_block = blockchain.chain[-1]
        other = Block(
            prev_block=prev_block,
            transactions=[
                invalid_txn
            ],
            reward=self.reward,
            difficulty=self.difficulty
        )
        with self.assertRaises(InvalidSignatureException):
            blockchain.verify_block(other)
