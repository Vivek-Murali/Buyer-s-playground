import uuid
from flask import session
from common.database import Database
import bcrypt

__author__ = 'jetfire'


class User(object):
    def __init__(self, email, username,password, first_name, last_name, gender, phone, picture,picture_name, likes, type,bal,status,_id=None):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.phone = phone
        self.username = username
        self.picture = picture
        self.picture_name = picture_name
        self.likes = likes
        self.type = type
        self.bal = bal
        self.status = status
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def get_by_email(cls, email):
        data = Database.find_one("user", {"email": email})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_id(cls, _id):
        data = Database.find_one("users", {"_id": _id})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_username(cls, username):
        data = Database.find_one("users", {"username": username})
        if data is not None:
            return cls(**data)

    @staticmethod
    def login_valid(username, password):
        # Check whether a user's email matches the password they sent us
        user = Database.find_one("users", {"username": username})
        # user = User.get_by_username(username)
        #print(user)
        if user is not None:
            password1 = bcrypt.checkpw(password.encode('utf-8'), user['password'])
            if(password1 == True):
                return True
        return False

    @classmethod
    def register(cls, email, username, password, first_name, last_name, gender, phone, picture,picture_name, likes,type,status,bal):
        user = cls.get_by_username(username)
        if user is None:
            hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            # User doesn't exist, so we can create it
            ''' Database.insert("users", {"email": email, "username": username, "password": hashpass, "first_Name": first_name, "last_name": last_name, "gender": gender, "phone": phone, "ava_hash":ava_hash})'''
            new_user = cls(email, username, hashpass, first_name, last_name, gender, phone, picture,picture_name,likes, type,status,bal)
            new_user.save_to_mongo()
            session['username'] = username
            return True
        else:
            # User exists :(
            return False

    @classmethod
    def update_user(cls,first_name, last_name, gender, phone, username):
        col1 = Database.DATABASE['users']
        col1.update_one({"username": username},{"$set": {"first_name,":first_name,"last_name":last_name,"gender":gender,"phone":phone}}, upsert=False)
        return True

    @staticmethod
    def reg_valid(username, email):
        # Check whether a user's email matches the password they sent us
        user = Database.find_one("users", {"username": username})
        email1 = Database.find_one("users", { "email" : email})
        # user = User.get_by_username(username)
        # print(user)
        if len(email1) > 0 or len(user) > 0:
            return True
        return False

    @staticmethod
    def login(username):
        # login_valid has already been called
        session['username'] = username
        session['logged_in'] = True
        data = Database.find_one("users", {"username": username})
        session['picture'] = data['picture']

    @staticmethod
    def logout():
        session['username'] = None
        session['logged_in'] = None
        session['picture'] = None
        if session:
            session.clear()

    def json(self):
        return {
            "email": self.email,
            "_id": self._id,
            "username":self.username,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "gender": self.gender,
            "phone": self.phone,
            "picture":self.picture,
            "picture_name":self.picture_name,
            "likes":[self.likes],
            "type":self.type,
            "status":self.status,
            "current_balance":self.bal
        }

    def save_to_mongo(self):
        Database.insert("users", self.json())

    @staticmethod
    def from_user_profile(username):
        return [post for post in
                Database.find(collection='users', query={'username': username})]
