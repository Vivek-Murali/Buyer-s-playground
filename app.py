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
from models.announcement import Anno
from twocheckout.error import TwocheckoutError
import twocheckout
import qrcode


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
    likes = None
    type = request.form['type']
    status = 1
    bal = 0
    mongo.save_file(photo.filename, photo)
    picture = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
    User.register(email, username, password, first_name, last_name, gender, phone, picture, photo.filename, likes, type,status,bal)
    flash("Registered Successfully", category='success')
    return render_template("register.html")


@app.route('/login')
def login_template():
    session.clear()
    return render_template('login.html')


@app.route('/user_home')
def user_home():
    return render_template('home.html', username=session['username'])


@app.route('/User_profile/<string:username>')
def user_profile(username):
    users = User.from_user_profile(username)
    return render_template('user_profile.html', username=session['username'], users=users)


@app.route('/edit_profile', methods=['POST'])
def edit_man():
        picture1 = session['picture']
        print(picture1)
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        phone = request.form['mobile']
        username = session['username']
        photo = request.files['file']
        col1 = Database.DATABASE['users']
        mongo.save_file(photo.filename, photo)
        col1.update_one({"username": username},
                        {"$set": {"first_name": first_name, "last_name": last_name, "gender": gender, "phone": phone, "picture_name":photo.filename}},
                        upsert=False)
        flash("Edited Successfully", category='success')
        return render_template('home.html', username=session['username'], picture =session['picture'])


@app.route('/edit_profile2')
def edit_template():
    return render_template('edit_profile.html', username=session['username'],
                           picture=session['picture'])


@app.route('/add_money')
def add_money_template():
    return render_template('addmoney.html', username=session['username'],
                           picture=session['picture'])


@app.route('/add_process', methods=['POST'])
def add_process_template():
    money = request.form['ammount']
    session['money'] = money
    return render_template('payout.html', username=session['username'],
                           money=session['money'])


@app.route('/order', methods=['POST'])
def order():
    # Setup credentials and environment
    twocheckout.Api.auth_credentials({
        'private_key': '4D22A936-A56C-4FDE-824B-5A606C5E0BD2',
        'seller_id': '901403850',
        'mode': 'sandbox'
    })
    print(request.form["token"])
    # Setup arguments for authorization request
    args = {
        'merchantOrderId': '123',
        'token': request.form["token"],
        'currency': 'USD',
        'total': '1.00',
        'billingAddr': {
            'name': 'Testing Tester',
            'addrLine1': '123 Test St',
            'city': 'Columbus',
            'state': 'OH',
            'zipCode': '43123',
            'country': 'USA',
            'email': 'example@2co.com',
            'phoneNumber': '555-555-5555'
        }
    }

    # Make authorization request
    try:
        result = twocheckout.Charge.authorize(args)
        return result.responseMsg
    except TwocheckoutError as error:
        return error.msg


@app.route('/insurance')
def insurance_template():
    return render_template("insurance.html", username=session['username'])


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
    print(user['type'])
    if user['type'] == 2:
        return render_template("home_admin.html", username=session['username'],user=user)
    elif user['type'] == 3:
        return render_template("home_auction.html", username=session['username'], user=user)
    elif user['type'] == 4:
        return render_template("home_logistic.html", username=session['username'], user=user)

    return render_template("home.html", username=session['username'],user=user)


@app.route('/logout')
def logout_user():
    User.logout()
    return render_template('index_home.html')


@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)


@app.route('/anno')
def anno():
    return render_template('anno.html')


@app.route('/view_user_all/<string:username>')
def user_post(username):
    posts = Anno.from_all_topic()
    return render_template('anno.html', posts=posts,
                           username=session['username'])


@app.route('/new_post/<string:username>', methods=['POST', 'GET'])
def new_post(username):
    if request.method == 'GET':
        return render_template('new_post.html', username=username)
    else:
        message = request.form['content']
        user = User.get_by_username(session['username'])
        likes = "0"
        new_post = Anno(message, user.username, user.picture_name, likes)
        new_post.save_to_mongo()
        username = session['username']
        return make_response(user_post(username))


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
        Database.insert('Assets', values)
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