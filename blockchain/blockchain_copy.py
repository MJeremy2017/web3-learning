import logging
import time
from typing import List
from dataclasses import dataclass
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from cryptography.hazmat.primitives import hashes, serialization
from utils import verify

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

    def sign(self, transaction: 'Transaction') -> 'Transaction':
        sig: bytes = self._private_key.sign(
            transaction.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        transaction.signature = sig.hex()
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


@dataclass
class Transaction:
    from_addr: PublicKey
    to_addr: PrivateKey
    amount: int
    signature: bytes = ''

    def __str__(self):
        return str(self.from_addr) + str(self.to_addr) + str(self.amount) + self.signature.hex()

    def encode(self):
        return (str(self.from_addr) + str(self.to_addr) + str(self.amount)).encode('utf-8')


def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    return PrivateKey(private_key), PublicKey(public_key)


class Wallet:
    def __init__(self):
        self.private_key, self.public_key = generate_key_pair()

    def sign(self, transaction: Transaction) -> Transaction:
        return self.private_key.sign(transaction)


class Block:
    def __init__(self, prev_hash: str, transactions: List[Transaction], reward: int, difficulty: int):
        self.prev_hash = prev_hash
        self.transactions = transactions
        self.reward = reward
        self.difficulty = difficulty
        self.nonce = 0
        self.block_hash = ""

    def mine(self, miner_addr: str):
        start_time = time.time()
        coinbase_transaction = self._generate_coinbase_transaction(self.reward, miner_addr)
        self.verify_transactions(self.transactions)
        while 1:
            block_hash = self._hash(
                self.prev_hash,
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

    def _generate_coinbase_transaction(self, reward: int, miner_addr: str) -> Transaction:
        # coinbase transaction does not need a signature
        return Transaction(
            from_addr="",
            to_addr=miner_addr,
            amount=reward,
        )

    def _hash(self,
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

    def _valid_block_hash(self, block_hash: str):
        return block_hash[:self.difficulty] == "0" * self.difficulty

    def verify_transactions(self, transactions: List[Transaction]):
        for txn in transactions:
            self._verify_signature(txn)

    def _verify_signature(self, txn: Transaction):
        public_key = txn.from_addr
        verify()
