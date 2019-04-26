import json
from time import time
import hashlib
from common.database import Database


class TransactionBlockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self,proof, previous_hash=None):


        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction_asset(self, username, user_id,amount, description):


        self.current_transactions.append({
            'username': username,
            'user_id': user_id,
            'amount': amount,
            'description': description
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):


        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):


        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):


        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @staticmethod
    def json(username, user_id,amount, description):
        return {
            'username': username,
            'user_id': user_id,
            'amount': amount,
            'description': description
        }

    @staticmethod
    def from_user_topic(username):
        return [post for post in
                Database.find(collection='Transaction_Normal', query=({'transactions.username': username},{'transactions':True}))]
