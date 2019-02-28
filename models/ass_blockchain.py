import json
from time import time
import hashlib
from common.database import Database
import pymongo


class AssetsBlockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self,proof, previous_hash=None):
        """
                Create a new Block in the Blockchain

                :param proof: <int> The proof given by the Proof of Work algorithm
                :param previous_hash: (Optional) <str> Hash of previous Block
                :return: <dict> New Block
                """

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

    def new_transaction_asset(self, username, user_id,filename, description):
        """
                Creates a new transaction to go into the next mined Block

                :param username: <str> Address of the Sender
                :param user_id: <str> ID of the Sender
                :param filename: <str> Asset of the Sender
                :param description: <str> Description of the Asset
                :return: <int> The index of the Block that will hold this transaction
                """

        self.current_transactions.append({
            'username': username,
            'user_id': user_id,
            'filename': filename,
            'description': description
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
                Creates a SHA-256 hash of a Block

                :param block: <dict> Block
                :return: <str>
                """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof

        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?

        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @staticmethod
    def json(username, user_id,filename, description):
        return {
            'username': username,
            'user_id': user_id,
            'filename': filename,
            'description': description
        }

    @staticmethod
    def from_user_topic(username):
        return [post for post in
                Database.find(collection='Assets', query=({'transactions.username': username},{'transactions':True}))]
