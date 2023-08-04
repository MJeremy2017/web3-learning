import random
import time
from unittest import TestCase
from typing import List
from blockchain_impl import Block, Transaction, Wallet, verify
from blockchain_impl import BlockChain, GenesisPublicKey
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


def generate_blockchain(length: int,
                        n_transactions: int = 2,
                        n_users: int = 3,
                        reward: int = 10,
                        difficulty: int = 1):
    wallets = [Wallet() for _ in range(n_users)]
    accounts = [100 for _ in range(n_users)]
    miner_addr = wallets[0].public_key

    def _get_transactions():
        nonlocal n_transactions, n_users
        txns = []
        for _ in range(n_transactions):
            sender_idx = random.randint(0, n_users - 1)
            while accounts[sender_idx] < 1:
                sender_idx = random.randint(0, n_users)
            receiver_idx = (sender_idx + 1) % n_users
            amount = random.randint(1, accounts[sender_idx] - 1)
            txn = generate_signed_transaction(
                wallets[sender_idx],
                wallets[receiver_idx],
                amount=amount
            )
            txns.append(txn)
            accounts[sender_idx] -= amount
            accounts[receiver_idx] += amount
        return txns

    prev_block = None
    chain = []
    first = True
    while length > 0:
        if first:
            block = Block(
                prev_block=prev_block,
                transactions=[Transaction(
                    from_addr=GenesisPublicKey(None),
                    to_addr=wallets[i].public_key,
                    amount=100
                ) for i in range(n_users)],
                reward=10,
                difficulty=1
            )
        else:
            block = Block(
                prev_block=prev_block,
                transactions=_get_transactions(),
                reward=10,
                difficulty=1
            )
        if not first:
            block.mine(miner_addr)
        if prev_block is not None:
            prev_block.next_block = block
        chain.append(block)
        prev_block = block
        length -= 1
        first = False
    return BlockChain(
        chain=chain,
        reward=reward,
        difficulty=difficulty
    ), accounts, wallets


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
        blockchain.add_transaction(
            generate_signed_transaction(
                wallets[0],
                wallets[1],
                amount=random.randint(1, accounts[0])
            )
        )
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
