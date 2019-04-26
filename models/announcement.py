import datetime
import uuid
from flask import session
from common.database import Database
import pymongo


class Anno(object):
    def __init__(self, message,username,picture,likes,anno_type,date_posted = datetime.datetime.now(), _id=None):
        self.message = message
        self.username = username
        self.picture = picture
        self.likes = likes
        self.anno_type = anno_type
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
    def from_all_noraml():
        return [post for post in Database.find(collection='post', query={'anno_type':'Normal'}).sort('date_posted', pymongo.DESCENDING)]

    @staticmethod
    def from_all_admin():
        return [post for post in Database.find(collection='post', query={'anno_type':'Admin'}).sort('date_posted', pymongo.DESCENDING)]

    @staticmethod
    def from_user_topic(username):
        return [post for post in Database.find(collection='post', query={'username':username}).sort('date_posted', pymongo.DESCENDING)]

    def json(self):
        return {
            '_id': self._id,
            'username': self.username,
            'message': self.message,
            'picture': self.picture,
            'anno_type':self.anno_type,
            'likes': [self.likes],
            'date_posted': self.date_posted
        }

    def save_to_mongo(self):
        Database.insert(collection='post',
                        data=self.json())

