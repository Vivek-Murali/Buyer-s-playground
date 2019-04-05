import uuid
from common.database import Database
import json
from time import time
import hashlib
__author__ = 'jetfire'


class Auction(object):
    def __init__(self,username,commodity_name,commodity_val,quantity,price,current_bid,bids,description,filename,date,_id=None):
        self.username = username
        self.commodity_name = commodity_name
        self.commodity_val = commodity_val
        self.quantity = quantity
        self.price = price
        self.current_bid = current_bid
        self.bids = bids
        self.description = description
        self.filename = filename
        self.date = date
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)
        self._id = uuid.uuid4().hex if _id is None else _id


    @classmethod
    def get_by_email(cls, email):
        data = Database.find_one("auction", {"email": email})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_id(cls, _id):
        data = Database.find_one("auction", {"_id": _id})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_username(cls, username):
        data = Database.find_one("auction", {"username": username})
        if data is not None:
            return cls(**data)

    @classmethod
    def create_new(cls,username,commodity_name,commodity_val,quantity,price,current_bid,bids,description,filename,date):
        new_auction = cls(username,commodity_name,commodity_val,quantity,price,current_bid,bids,description,filename,date)
        new_auction.save_to_mongo()
        return True

    def json1(self):
        return {
            "_id": self._id,
            'username':self.username,
            'commodity_name':self.commodity_name,
            'commodity_value':self.commodity_val,
            'quantity':self.quantity,
            'price':self.price,
            'current_bid':self.current_bid,
            'bids':self.bids,
            'description':self.description,
            'image':self.filename,
            'created_date':self.date
        }

    def save_to_mongo(self):
        Database.insert("auction", self.json1())

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

    def new_transaction_asset(self, username, auction_id,bid, price, quantity,commodity_name, commodity_val):
        self.current_transactions.append({
            'username': username,
            'auction_id': auction_id,
            'bid': bid,
            'price': price,
            'quantity':quantity,
            'commodity_name':commodity_name,
            'commodity_val':commodity_val
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
    def json(username, auction_id,bid, price, quantity,commodity_name, commodity_val):
        return {
            'username': username,
            'auction_id': auction_id,
            'bid': bid,
            'price': price,
            'quantity':quantity,
            'commodity_name':commodity_name,
            'commodity_val':commodity_val
        }

    @staticmethod
    def from_user_topic(username):
        return [post for post in
                Database.find(collection='Bids', query=({'transactions.username': username},{'transactions':True}))]

    @staticmethod
    def from_user_profile(username):
        return [post for post in
                Database.find(collection='users', query={'username': username})]