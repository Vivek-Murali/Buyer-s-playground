__author__ = 'Jetfire'


from flask import Flask, render_template, request, session, make_response, flash, jsonify
#from flask_avatars import Avatars
import hashlib
import datetime
import base64
from models.users import User
from common.database import Database
from flask_pymongo import PyMongo
from models.blockchain import Blockchain
from models.ass_blockchain import AssetsBlockchain
from uuid import uuid4
import pandas as pd

app = Flask(__name__)  # '__main__'
app.secret_key = "Hero"
app.config['MONGO_URI']= "mongodb://jetfire:vivek95@ds161410.mlab.com:61410/buyer"
mongo = PyMongo(app)
#avatars = Avatars(app)
BASECOORD = [22.3511148, 78.6677428]
blockchain = Blockchain()
ablockchain = AssetsBlockchain()
node_identifier = str(uuid4()).replace('-', '')


@app.before_first_request
def initialize_database():
    Database.initialize()


@app.route('/index_template')
def index_template1():
    session.clear()
    return render_template('index_home.html')


@app.route('/')
def index_template():
    session.clear()
    return render_template('index.html')


@app.route('/register')
def register_template():
    return render_template('register.html')


@app.route('/auth_register', methods=['POST'])
def register_user():
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    gender = request.form['gender']
    phone = request.form['mobile']
    photo = request.files['file']
    mongo.save_file(photo.filename, photo)
    picture = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
    User.register(email, username, password, first_name, last_name, gender, phone, picture, photo.filename)
    flash("Registered Successfully", category='success')
    return render_template("register.html")


@app.route('/login')
def login_template():
    session.clear()
    return render_template('login.html')


@app.route('/user_home')
def user_home():
    return render_template('home.html', username=session['username'])


@app.route('/auth_login', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']

    if User.login_valid(username, password):
        User.login(username)
    else:
        session['username'] = None
        return render_template("index_home.html")

    user = mongo.db.users.find_one_or_404({'username':username})

    return render_template("home.html", username=session['username'],user=user)


@app.route('/logout')
def logout_user():
    User.logout()
    return render_template('index_home.html')


@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)


@app.route('/auction')
def auction_template():
    render_template('auction.html', username=session['username'])


@app.route('/assets/<string:username>')
@app.route('/assets')
def assets(username):
    if username is not None:
        user = User.get_by_username(username)
    else:
        user = User.get_by_username(session['username'])
        file_name = Database.find("Assets",{'username':user.username})
    posts = [post for post in
                mongo.db.Assets.find({'username': user.username},{ '_id':False})]
    return render_template("assets.html", username=user.username, posts=posts)


@app.route('/asset')
def asset_template():
    return render_template("assets.html", username=session['username'])


@app.route('/assets_template', methods=['POST', 'GET'])
def create_new_asset():
    if request.method == 'GET':
        return render_template('assets.html')
    else:
        description = request.form['description']
        file1 = request.files['file']
        user = User.get_by_username(session['username'])
        values = AssetsBlockchain.json(user.username,user._id,file1.filename,description)
        # Check that the required fields are in the POST'ed data
        required = ['username', 'user_id','filename','description']
        if not all(k in values for k in required):
            return 'Missing values', 400
        # Create a new Transaction
        index = ablockchain.new_transaction_asset(values['username'], values['user_id'],values['filename'],values['description'])
        response = {'message': f'Transaction will be added to Block {index}'}
        result = jsonify(response)
        last_block = ablockchain.last_block
        last_proof = last_block['proof']
        proof = ablockchain.proof_of_work(last_proof)

        # Forge the new Block by adding it to the chain
        previous_hash = blockchain.hash(last_block)
        block = ablockchain.new_block(proof, previous_hash)

        response = {
            'node_id':node_identifier,
            'message': "New Block Forged",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
        }
        Database.insert('Assets_block', response)
        Database.insert('Assets',values)
        mongo.save_file(file1.filename, file1)
        flash("Posted Successfully", category='success')
        return make_response(assets(user.username))


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        filename=node_identifier,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'filename']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['filename'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(port=5001, debug=True)