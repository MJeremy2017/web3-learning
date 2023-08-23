from utils import unpickle_wallets, unpickle_accounts, generate_signed_transaction
from client_utils import add_transaction, mine_block
import random

HOST = 'http://localhost'
PORT = 5000


if __name__ == '__main__':
    accounts = unpickle_accounts('tmp/accounts')
    wallets = unpickle_wallets('tmp/wallets')

    wa = wallets[0]
    wb = wallets[1]
    amount = random.randint(1, accounts[0])
    txn = generate_signed_transaction(wa, wb, amount)
    print('txn', txn)
    add_transaction(
        host=HOST,
        port=PORT,
        sender=str(txn.from_addr),
        receiver=str(txn.to_addr),
        signature=txn.signature,
        amount=txn.amount)

    mine_block(
        host=HOST,
        port=PORT,
        miner=str(txn.from_addr)
    )