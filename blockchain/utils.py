from blockchain_copy import Transaction
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature


def verify(public_key: RSAPublicKey, transaction: Transaction) -> bool:
    try:
        public_key.verify(
            signature=bytes.fromhex(transaction.signature),
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
