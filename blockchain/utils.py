from blockchain_impl import Block, Transaction, Wallet, BlockChain
from custom_types import GenesisPublicKey, PublicKey, PrivateKey
from cryptography.hazmat.primitives import serialization
import random
from typing import List
import pickle
import secrets
import time


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
            while accounts[sender_idx] <= 1:
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


def deserialize_public_key(data: str) -> PublicKey:
    return PublicKey(serialization.load_pem_public_key(data.encode('utf-8')))


def deserialize_private_key(data: str) -> PrivateKey:
    return PrivateKey(serialization.load_pem_private_key(data.encode('utf-8'), password=None))


def pickle_wallets(wallets: List[Wallet]):
    wallets_serial = []
    for w in wallets:
        wallets_serial.append((str(w.public_key), str(w.private_key)))
    with open('tmp/wallets', 'wb') as f:
        pickle.dump(wallets_serial, f)


def unpickle_wallets(file: str) -> List[Wallet]:
    with open(file, 'rb') as f:
        wallets_serial = pickle.load(f)
    wallets = []
    for w in wallets_serial:
        wd = Wallet(public_key=deserialize_public_key(w[0]), private_key=deserialize_private_key(w[1]))
        wallets.append(wd)
    return wallets


def pickle_accounts(accounts: List[int]):
    with open('tmp/accounts', 'wb') as f:
        pickle.dump(accounts, f)


def unpickle_accounts(file: str) -> List[int]:
    with open(file, 'rb') as f:
        accounts = pickle.load(f)
    return accounts


def save_accounts_and_wallets(accounts: List[int], wallets: List[Wallet]):
    pickle_accounts(accounts)
    pickle_wallets(wallets)
