import datetime
import uuid
from flask import session
from common.database import Database
from flask_pymongo import PyMongo, pymongo


class Post(object):
    def __init__(self, message, topic_id,username, picture,date_posted = datetime.datetime.now(), _id=None):
        self.message = message
        self.topic_id = topic_id
        self.username = username
        self.picture = picture
        self.date_posted = date_posted
        self._id = uuid.uuid4().hex  if _id is None else _id

    @classmethod
    def get_post_by_id(cls, _id):
        data = Database.find_one("post", {"_id": _id})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_post_by_username(cls, username):
        data = Database.find_one("post", {"username":username})
        if data is not None:
            return cls(**data)

    @classmethod
    def post_chirp(cls, message, username, tag, date_posted):
        username = session['username']
        picture = session['picture']
        Database.insert("post", {"message": message, "username": username, "tag": tag, "picture": picture, "date_posted": date_posted})
        session['username'] = username
        return True

    @classmethod
    def show_chrip(cls):
        posts = Database.find('post', {})
        print(posts)
        return posts

    @classmethod
    def from_mongo(cls, id):
        post_data = Database.find_one(collection='post', query={'_id': id})
        return cls(**post_data)

    @staticmethod
    def from_all_topic():
        return [post for post in Database.find(collection='post', query={}).sort('date_posted', pymongo.DESCENDING)]

    @staticmethod
    def from_user_topic(username):
        return [post for post in Database.find(collection='post', query={'username':username}).sort('date_posted', pymongo.DESCENDING)]

    @staticmethod
    def from_topic(_id):
        return [post for post in Database.find(collection='post', query={'topic_id': _id}).sort('date_posted', pymongo.DESCENDING)]

    def json(self):
        return {
            '_id': self._id,
            'topic_id': self.topic_id,
            'username': self.username,
            'message': self.message,
            'picture':self.picture,
            'date_posted': self.date_posted
        }

    def save_to_mongo(self):
        Database.insert(collection='post',
                        data=self.json())