from flask import Flask, request, jsonify
from blockchain_impl import BlockChain, Transaction
from utils import generate_blockchain, deserialize_public_key, save_accounts_and_wallets
import fire
import base64

app = Flask(__name__)
blockchain: BlockChain = None


@app.route('/blockchain/info', methods=['GET'])
def chain_info():
    return jsonify({
        'message':
            {
                'chain_length': len(blockchain.chain),
                'pending_transactions': len(blockchain.pending_transactions),
                'reward': blockchain.reward,
                'difficulty': blockchain.difficulty,
                'peers': blockchain.peers
            }
    }), 200


@app.route('/blockchain/mine', methods=['GET'])
def mine():
    pass


@app.route('/transaction/new', methods=['POST'])
def add_new_transaction():
    try:
        data = request.get_json()
        sender: str = str(data['sender'])
        receiver: str = str(data['receiver'])
        amount: int = int(data['amount'])
        signature: bytes = base64.b64decode(data['signature'])
        txn = Transaction(
            deserialize_public_key(sender),
            deserialize_public_key(receiver),
            amount,
            signature
        )
        blockchain.add_transaction(txn)
        return jsonify({'message': "Transaction added successfully"}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except KeyError as e:
        return jsonify({'error': f'Missing key {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error {e}'}), 500


def main(port=5000, peer=5001, reward=10, difficulty=1):
    global blockchain
    blockchain, accounts, wallets = generate_blockchain(3, 5, 3, reward=reward, difficulty=difficulty)
    blockchain.add_peer(('http://localhost', peer))

    save_accounts_and_wallets(accounts, wallets)
    print('chain info:', blockchain.difficulty, blockchain.peers)

    app.run(debug=True, port=port)


if __name__ == '__main__':
    fire.Fire(main)
