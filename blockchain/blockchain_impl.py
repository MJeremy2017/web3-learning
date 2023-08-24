from __future__ import annotations
from cryptography.exceptions import InvalidSignature
import logging
import time
from typing import List, Union, Tuple
from dataclasses import dataclass
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from cryptography.hazmat.primitives import hashes, serialization
from exceptions import *
from client_utils import add_transaction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PrivateKey:
    def __init__(self, key: RSAPrivateKey):
        self._private_key = key

    def __str__(self):
        key_bytes = self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        return key_bytes.decode('utf-8')

    def sign(self, transaction: Transaction) -> Transaction:
        sig: bytes = self._private_key.sign(
            transaction.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        transaction.signature = sig
        return transaction


class PublicKey:
    def __init__(self, key: RSAPublicKey):
        self._public_key = key

    def __str__(self):
        key_bytes = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return key_bytes.decode('utf-8')

    @property
    def public_key(self):
        return self._public_key

    def __eq__(self, other: PublicKey):
        return str(self) == str(other)


class GenesisPublicKey(PublicKey):
    def __init__(self, key: RSAPublicKey):
        super().__init__(key)

    def __str__(self):
        return ""


@dataclass
class Transaction:
    from_addr: PublicKey
    to_addr: PublicKey
    amount: int
    signature: bytes = b''
    ts: int = int(time.time())

    def __str__(self):
        return str(self.from_addr) + str(self.to_addr) + str(self.amount) + self.signature.hex()

    def encode(self):
        return (str(self.from_addr) + str(self.to_addr) + str(self.amount)).encode('utf-8')

    def __eq__(self, other: Transaction):
        return self.amount == other.amount and str(self.from_addr) == str(other.from_addr) \
            and str(self.to_addr) == str(other.to_addr) and self.signature == other.signature


def _generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    return PrivateKey(private_key), PublicKey(public_key)


def hash_block(
        prev_hash: str,
        transactions: List[Transaction],
        coinbase_transaction: Transaction,
        nonce: int) -> str:
    encode_str = prev_hash
    for txn in transactions + [coinbase_transaction]:
        encode_str += str(txn)
    encode_str += str(nonce)
    encode_str = encode_str.encode()
    return hashlib.sha256(encode_str).hexdigest()


def verify_transaction_has_sufficient_funds(block: Block, txn: Transaction):
    from_addr = txn.from_addr
    amount = txn.amount
    balance = 0
    transactions = block.transactions

    i = 0
    # transactions are already sorted
    while transactions[i] != txn:
        if transactions[i].from_addr == from_addr:
            balance -= transactions[i].amount
        if transactions[i].to_addr == from_addr:
            balance += transactions[i].amount
        i += 1

    node: Block = block.prev_block
    while node:
        for txn in node.transactions:
            if txn.from_addr == from_addr:
                balance -= txn.amount
            if txn.to_addr == from_addr:
                balance += txn.amount
        node = node.prev_block
    if balance < amount:
        raise InsufficientFundsException(f"transfer amount {amount}, got balance {balance}")


class Wallet:
    def __init__(self, public_key=None, private_key=None):
        if public_key is None or private_key is None:
            self.private_key, self.public_key = _generate_key_pair()
        else:
            self.public_key = public_key
            self.private_key = private_key

    def sign(self, transaction: Transaction) -> Transaction:
        return self.private_key.sign(transaction)


class Block:
    def __init__(self, prev_block: Union[Block, None], transactions: List[Transaction], reward: int, difficulty: int):
        self.prev_block = prev_block
        self.next_block = None
        self.transactions = transactions
        self.reward = reward
        self.difficulty = difficulty
        self.nonce = 0
        self.block_hash = "0x0"
        self.transactions.sort(key=lambda x: x.ts)
        self.coin_base_transaction = None

    def mine(self, miner_addr: PublicKey):
        start_time = time.time()
        coinbase_transaction = self._generate_coinbase_transaction(self.reward, miner_addr)
        self.verify_valid_transactions(self.transactions)
        while 1:
            block_hash = hash_block(
                self.prev_block.block_hash,
                self.transactions,
                coinbase_transaction,
                self.nonce
            )
            if self._valid_block_hash(block_hash):
                time_cost = time.time() - start_time
                self.block_hash = block_hash
                logging.info(f"Block hash {self.block_hash}, mined time cost {time_cost}")
                break
            else:
                self.nonce += 1

    def _generate_coinbase_transaction(self, reward: int, miner_addr: PublicKey) -> Transaction:
        # coinbase transaction does not need a signature
        if self.coin_base_transaction is None:
            self.coin_base_transaction = Transaction(
                from_addr=GenesisPublicKey(None),
                to_addr=miner_addr,
                amount=reward,
            )
        return self.coin_base_transaction

    def _valid_block_hash(self, block_hash: str):
        return block_hash[:self.difficulty] == "0" * self.difficulty

    def verify_valid_transactions(self, transactions: List[Transaction]):
        for txn in transactions:
            self.verify_single_transaction(txn)

    def verify_single_transaction(self, txn: Transaction):
        self.verify_signature(txn)
        verify_transaction_has_sufficient_funds(self, txn)

    def verify_signature(self, txn: Transaction):
        public_key: PublicKey = txn.from_addr
        is_valid_txn = verify(public_key, txn)
        if not is_valid_txn:
            raise InvalidSignatureException(f"Invalid transaction {txn}")

    def verify_correct_reward(self, other: Block):
        if self.reward != other.reward:
            raise ValueError(f"Invalid reward for miner, expecting {self.reward} got {other.reward}")

    def verify_correct_transactions(self, other: Block):
        self.verify_transaction_fields(other.transactions)
        self.verify_valid_transactions(other.transactions)

    def verify_transaction_fields(self, transactions: List[Transaction]):
        sorted_txns = sorted(transactions, key=lambda x: x.ts)
        if len(transactions) != len(self.transactions):
            raise ValueError("Unequal number of transactions")
        for i in range(len(sorted_txns)):
            if self.transactions[i] != sorted_txns[i]:
                raise ValueError("Unequal transaction fields")


class BlockChain:
    """
    1. save/add the pending transactions
    2. add and validate a new block
    """

    def __init__(self, chain: List[Block], reward: int, difficulty: int, peers: List[Tuple] = None):
        self.reward = reward
        self.difficulty = difficulty
        self.pending_transactions: List[Transaction] = []
        self.chain: List[Block] = chain
        self.peers: List = peers if peers else []

    def add_transaction(self, transaction: Transaction):
        print("pending transaction len", len(self.pending_transactions))
        for current_txn in self.pending_transactions:
            if transaction == current_txn:
                return
        self.pending_transactions.append(transaction)
        self.broadcast_transaction(transaction)

    def mine(self, miner_addr: PublicKey):
        last_block = self.chain[-1]
        block_new = Block(
            prev_block=last_block,
            transactions=self.pending_transactions,
            reward=self.reward,
            difficulty=self.difficulty
        )
        try:
            block_new.mine(miner_addr)
            self.add_block(block_new, need_verify=False)
            self.pending_transactions = []
        except Exception as e:
            print(f"Failed to mine {e}")

    def add_block(self, block: Block, need_verify=False):
        if need_verify:
            try:
                self.verify_block(block)
            except Exception as e:
                print(f"Invalid block {e}")
        last_block = self.chain[-1]
        last_block.next_block = block
        self.chain.append(block)

    def verify_block(self, other: Block):
        self.verify_correct_reward(other)
        self.verify_correct_transactions(other)
        self.verify_block_hash(other)

    def verify_correct_reward(self, other: Block):
        if self.reward != other.reward:
            raise ValueError(f"Invalid reward for miner, expecting {self.reward} got {other.reward}")

    def verify_correct_transactions(self, other: Block):
        self.verify_valid_transactions(other)

    def verify_block_hash(self, other: Block):
        calculated_hash = hash_block(
            prev_hash=other.prev_block.block_hash,
            transactions=other.transactions,
            coinbase_transaction=other.coin_base_transaction,
            nonce=other.nonce
        )
        if other.block_hash != calculated_hash:
            raise ValueError(f"Wrong block hash, expected hash {calculated_hash} got hash {other.block_hash}")

        if self.difficulty != other.difficulty:
            raise ValueError(
                f"Wrong difficulty, expected difficulty {self.difficulty} got difficulty {other.difficulty}")

        # verify difficulty and hash correct
        if other.block_hash[:self.difficulty] != "0" * self.difficulty:
            raise ValueError(f"Wrong block {other.block_hash} with difficulty {self.difficulty}")

    def verify_valid_transactions(self, block: Block):
        transactions = block.transactions
        for txn in transactions:
            self.verify_single_transaction(block, txn)

    def verify_single_transaction(self, block: Block, txn: Transaction):
        self.verify_signature(txn)
        verify_transaction_has_sufficient_funds(block, txn)

    def verify_signature(self, txn: Transaction):
        public_key: PublicKey = txn.from_addr
        is_valid_txn = verify(public_key, txn)
        if not is_valid_txn:
            raise InvalidSignatureException(f"Invalid transaction {txn}")

    def add_peer(self, peer: Tuple):
        self.peers.append(peer)

    def broadcast_transaction(self, transaction: Transaction):
        print('peers', self.peers)
        for peer in self.peers:
            host, port = peer[0], peer[1]
            print("broadcasting transaction", host, port)
            add_transaction(
                host=host,
                port=port,
                sender=str(transaction.from_addr),
                receiver=str(transaction.to_addr),
                amount=transaction.amount,
                signature=transaction.signature)


def verify(public_key: PublicKey, transaction: Transaction) -> bool:
    try:
        public_key.public_key.verify(
            signature=transaction.signature,
            data=transaction.encode(),
            padding=padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            algorithm=hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False


if __name__ == '__main__':
    wallets = [Wallet() for _ in range(3)]

    genesis_block = Block(
        prev_block=None,
        transactions=[
            Transaction(
                from_addr=GenesisPublicKey(None),
                to_addr=wallets[i].public_key,
                amount=100
            ) for i in range(3)
        ],
        reward=10,
        difficulty=1
    )

    chain = [genesis_block]

    block_chain = BlockChain(chain=chain, reward=10, difficulty=1)
    txn1 = Transaction(
        wallets[0].public_key,
        wallets[1].public_key,
        amount=10,
    )
    signed_txn1 = wallets[0].sign(txn1)
    block_chain.add_transaction(signed_txn1)

    txn2 = Transaction(
        wallets[0].public_key,
        wallets[2].public_key,
        amount=10,
    )
    signed_txn2 = wallets[0].sign(txn2)
    block_chain.add_transaction(signed_txn2)

    block_chain.mine(wallets[2].public_key)
    print("chain length", len(block_chain.chain))
