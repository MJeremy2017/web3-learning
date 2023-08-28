from __future__ import annotations  # postpone type evaluation until explicitly invoked
import time
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from cryptography.hazmat.primitives import hashes, serialization


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


class Wallet:
    def __init__(self, public_key=None, private_key=None):
        if public_key is None or private_key is None:
            self.private_key, self.public_key = _generate_key_pair()
        else:
            self.public_key = public_key
            self.private_key = private_key

    def sign(self, transaction: Transaction) -> Transaction:
        return self.private_key.sign(transaction)


def _generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    return PrivateKey(private_key), PublicKey(public_key)
