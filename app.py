__author__ = 'Jetfire'


from flask import Flask, render_template, request, session, make_response, flash, jsonify
from flask_mail import Mail,Message
import hashlib
import datetime
from models.users import User
from common.database import Database
from flask_pymongo import PyMongo
from models.blockchain import Blockchain
from models.ass_blockchain import AssetsBlockchain
from models.auction import Auction
from models.Scrapping_with_classs import Check
from selenium.common.exceptions import WebDriverException
from uuid import uuid4
import pymongo
from models.announcement import Anno
import stripe


app = Flask(__name__)  # '__main__'
app.secret_key = "Hero"
app.config['MONGO_DBNAME']="heroku_hnv16g8k"
app.config['MONGO_URI']= "mongodb://jetfire:vivek95@ds043477.mlab.com:43477/heroku_hnv16g8k"
mail_settings = {
        "MAIL_SERVER":'smtp.gmail.com',
        "MAIL_USE_TLS":False,
        "MAIL_USE_SSL":True,
        "MAIL_PORT":465,
        "MAIL_USERNAME":'007ottaku@gmail.com',
        "MAIL_PASSWORD":'77588870'
}
app.config.update(mail_settings)
mail = Mail(app)
mongo = PyMongo(app)
#avatars = Avatars(app)
BASECOORD = [22.3511148, 78.6677428]
blockchain = Blockchain()
ablockchain = AssetsBlockchain()
node_identifier = str(uuid4()).replace('-', '')
stripe_keys = {
  'secret_key': "sk_test_lRubQfxlGGUAHqZQzpJ78M8u",
  'publishable_key':"pk_test_he7jrXDbjsKMIR1JofcmzCnH"
}

stripe.api_key = stripe_keys['secret_key']


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
    date  = request.form['date']
    likes = None
    type = "1"
    bal = 0
    status = 1
    lo_time = datetime.datetime.utcnow()
    re_time = datetime.datetime.utcnow()
    filename = uuid4().hex + photo.filename
    picture = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
    user = User.get_by_username(username)
    emailval = User.get_by_email(email)
    if user is not None or emailval is not None:
        flash("Username or Email taken", category='warning')
        return make_response(register_template())
    else:
        mongo.save_file(filename, photo)
        User.register(email, username, password, first_name, last_name, gender, phone, picture, filename, likes, type,status,bal,date,lo_time,re_time)
        flash("Registered Successfully", category='success')
        return make_response(login_template())


@app.route('/login')
def login_template():
    session.clear()
    return render_template('login.html')


@app.route('/user_home')
def user_home():
    return render_template('home.html', username=session['username'])


@app.route('/req_auc')
def req_auc():
    return render_template('auction_req.html', username=session['username'])


@app.route('/admin_home')
def admin_home():
    return render_template('Admin_home.html', username=session['username'])


@app.route('/list_admin')
def list_admin():
    return render_template('lists.html', username=session['username'])


@app.route('/list_product_temp')
def list_products_temp():
    return render_template('list-products.html', username=session['username'])


@app.route('/list_product',methods=['POST'])
def list_products():
    name = request.form['name']
    if name == 'All':
        lists = [post for post in
                 Database.find(collection='products', query={})]
        print(lists)
    else:
        lists = [post for post in Database.find(collection='products', query={'commodity':name})]
        print(lists)
    return render_template("list-products.html", username=session['username'], lists=lists)


@app.route('/list_users_temp')
def list_users_temp():
    return render_template('all_users.html', username=session['username'])


@app.route('/list_insurance_temp')
def list_insurance_temp():
    return render_template('list-insurance.html', username=session['username'])


@app.route('/User_profile/<string:username>')
def user_profile(username):
    users = User.from_user_profile(username)
    return render_template('user_profile.html', username=session['username'], users=users)


@app.route('/edit_profile', methods=['POST'])
def edit_man():
        picture1 = session['picture']
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
                           money=session['money'], key=stripe_keys['publishable_key'])


@app.route('/charge', methods=['POST'])
def charge():
    # Amount in cents
    amount = int(session['money'])
    username = session['username']
    card_number = request.form['cno']
    exp_month = request.form['expMonth']
    exp_year = request.form['expYear']
    cvv_no = request.form['cvv']
    des = "Added Money to Wallet"
    token = stripe.Token.create(
        card={
            "number": card_number,
            "exp_month": exp_month,
            "exp_year": exp_year,
            "cvc": cvv_no
        },
    )
    user = mongo.db.users.find_one_or_404({'username': username})
    customer = stripe.Customer.create(
        email=user['email'],
        source=token
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='inr',
        description='Flask Charge'
    )
    Database.insert('Transaction_Normal', {"token_id": token, "username": username, "email": user['email'], "amount": amount,
                                    "description": des})
    col1 = Database.DATABASE['users']
    col1.update_one({"username": username},
                    {"$inc": {"bal":amount}},
                    upsert=False)
    flash("Added Successfully", category='success')

    return make_response(user_profile(username))


@app.route('/insurance')
def insurance_template():
    return render_template("insurance.html", username=session['username'])


@app.route('/insurance_create')
def insurance_template_create():
    return render_template("insurace_create.html", username=session['username'])


@app.route('/insurance_reg', methods=['POST'])
def insurance_template_reg():
    name = request.form['name']
    description = request.form['description']
    type = request.form['type']
    url =  request.form['url']
    Database.insert('insurance', {'name':name,'description': description, 'type':type, 'url':url})
    return render_template("insurace_create.html", username=session['username'])


@app.route('/insurance_all', methods=['POST'])
def insurance_template_all():
    name = request.form['name']
    if name == 'All':
        lists = [post for post in
                 Database.find(collection='insurance', query={})]
    else:
        lists = [post for post in Database.find(collection='insurance', query={'name': name})]
    return render_template("list-insurance.html", username=session['username'], lists=lists)


@app.route('/user_all', methods=['POST'])
def user_template_all():
    name = request.form['name']
    if name == 'All':
        lists = [post for post in
                 Database.find(collection='users', query={})]
    else:
        lists = [post for post in Database.find(collection='users', query={'username': name})]
    return render_template("all_users.html", username=session['username'], lists=lists)


@app.route('/edit_profile_admin', methods=['POST'])
def edit_man_admin():
        picture1 = session['picture']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        phone = request.form['mobile']
        username = session['username']
        photo = request.files['file']
        status = request.form['status']
        type1 = request.form['type']
        col1 = Database.DATABASE['users']
        mongo.save_file(photo.filename, photo)
        col1.update_one({"username": username},
                        {"$set": {"first_name": first_name, "last_name": last_name, "gender": gender, "phone": phone, "picture_name":photo.filename, "status":status, "type":type1}},
                        upsert=False)
        flash("Edited Successfully", category='success')
        return render_template('all_users.html', username=session['username'], picture =session['picture'])


@app.route('/edit_profile3')
def edit_template_admin():
    return render_template('admin_user_edit.html', username=session['username'],
                           picture=session['picture'])


@app.route('/auth_login', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']

    if User.login_valid(username, password):
        User.login(username)
    else:
        u = Database.find_one('users', {'username':username})
        with app.app_context():
            msg = Message(sender=app.config.get("MAIL_USERNAME"),recipients=[u['email']])
            msg.subject = "Buysplyground Authentication Error"
            msg.body = """Someone tried to login"""
            mail.send(msg)
            flash("Incorrect Username or Password ", category='danger')
            session['username'] = None
        return make_response(login_template())

    user = mongo.db.users.find_one_or_404({'username':username})
    lo_time1 = datetime.datetime.utcnow()
    lo_time = lo_time1.ctime()
    col1 = Database.DATABASE['users']
    col1.update_one({"username": username},
                    {"$set": {"last_login":lo_time}},
                    upsert=False)
    session['type'] = user['type']
    session['status'] = user['status']
    if user['type'] == 2:
        return render_template("Admin_home.html", username=session['username'], user=user)
    elif user['type'] == 4:
        return render_template("home_logistic.html", username=session['username'], user=user)
    else:
        return render_template("home.html", username=session['username'], user=user,)


@app.route('/logout')
def logout_user():
    User.logout()
    return make_response(index_template())


@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)


@app.route('/anno')
def anno():
    return render_template('anno.html')


@app.route('/admin_request')
def admin_req():
    posts = [post for post in
     Database.find(collection='requests', query={}).sort('date_posted', pymongo.DESCENDING)]
    return render_template('admin_auction.html', posts=posts, username=session['username'])


@app.route('/accept_req/<string:username>')
def accept_req(username):
    col1 = Database.DATABASE['requests']
    col1.update_one({"username": username},
                    {"$set": {"status": "Approved"}},
                    upsert=False)
    col2 = Database.DATABASE['users']
    col2.update_one({"username": username},
                    {"$set": {"type": "3"}},
                    upsert=False)
    return make_response(admin_home())


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
    return render_template('auction.html', username=session['username'])


@app.route('/auction_home')
def auction_home_template():
    return render_template('auction_home.html', username=session['username'])


@app.route('/bid_home')
def bid_home_template():
    posts = Auction.from_all_auction()
    return render_template('biding_area.html', username=session['username'], posts=posts)


@app.route('/auction_create', methods=['POST'])
def auction_create():
    commodity_name = request.form['comname']
    username = session['username']
    com = Database.find_one('products', {'commodity': commodity_name})
    commodity_val = com['value']
    quantity = request.form['Quantity']
    price = request.form['price']
    current_bid = 0
    bids = []
    description = request.form['description']
    date = datetime.datetime.now()
    date = date.strftime('%d-%m-%y')
    image = request.files['image']
    filename = uuid4().hex + image.filename
    mongo.save_file(filename, image)
    Auction.create_new(username,commodity_name,commodity_val,quantity,price,current_bid,bids,description,filename,date)
    flash("Created Successfully", category='success')
    return make_response(auction_home_template())


@app.route('/auctions/<string:username>')
@app.route('/auctions')
def auctions(username):
    if username is not None:
        user = User.get_by_username(username)
    else:
        user = User.get_by_username(session['username'])
        auction_list = Database.find("auction", {'username': user.username})
    posts = [post for post in
                mongo.db.auction.find({'username': user.username}, {'_id': False})]
    return render_template("auction_details.html", username=user.username, posts=posts)


@app.route('/fetch_temp')
def fetch_home():
    return render_template('fetch_data.html', username=session['username'])


@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    commodity_name = request.form['comname']
    month = request.form['month']
    com = Database.find_one('products', {'commodity': commodity_name})
    commodity_val = str(com['value'])
    print(type(commodity_val))
    year = request.form['year']
    try:
        Check.check(month,year,commodity_val)
    except WebDriverException:
        pass
    flash("Data Pushed Successfully", category='success')
    return make_response(admin_home())


@app.route('/auction_req1', methods=['POST'])
def auction_req_template():
    des = request.form['description']
    username = session['username']
    user = Database.find_one('users', {'username': username})
    type = user['type']
    date_req = datetime.datetime.utcnow()
    col1 = Database.DATABASE['users']
    col1.update_one({"username": username},
                    {"$set": {"status":1}},
                    upsert=False)
    req_check = Database.find_one('requests', {'username': username})
    if req_check is not None:
        session['status'] = user['status']
        return render_template('auction_req.html', username=session['username'])
    else:
        Database.insert('requests',{"username":username,"descriptions":des,"type":type, "date":date_req})
        session['type'] = type
        session['status'] = user['status']
        flash("Requested Successfully", category='success')
        return make_response(user_home())


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
        index = ablockchain.new_transaction_asset(values['username'], values['user_id'],
                                                  values['filename'], values['description'])
        response = {'message': f'Transaction will be added to Block {index}'}
        result = jsonify(response)
        last_block = ablockchain.last_block
        last_proof = last_block['proof']
        proof = ablockchain.proof_of_work(last_proof)

        # Forge the new Block by adding it to the chain
        previous_hash = blockchain.hash(last_block)
        block = ablockchain.new_block(proof, previous_hash)

        response = {
            'node_id': node_identifier,
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
    app.run(port=5003, debug=True)
