import pymongo
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.spatial import KDTree
from pymongo import GEO2D
from bson.son import SON
import json
import pickle
import statsmodels.api as sm
from common.database import Database
conn = pymongo.MongoClient('mongodb://jetfire:vivek95@ds043477.mlab.com:43477/heroku_hnv16g8k')
db = conn['heroku_hnv16g8k']


class MlModel:
    @staticmethod
    def filter_based(data):
        db.ecom.create_index([("geolocation", GEO2D)])
        query = {"geolocation": SON([("$near", data), ("$maxDistance", 1000)])}
        posts = [post for post in db.ecom.find(query)]
        print(posts)
        return posts

    @staticmethod
    def recon_based():
        b = db.products.find()
        a = db.rating.find()
        db.Recommendation.drop()
        df = pd.DataFrame(list(a))
        df1 = pd.DataFrame(list(b))
        p = df.groupby(['rating', 'com_value', 'id']).sum().reset_index().groupby(['id']).mean()
        q = df.groupby(['rating', 'com_value', 'id']).sum().reset_index().groupby(['com_value']).mean()
        r = df1
        r = r.set_index(r['value'])
        r = r.sort_index()
        df = df.set_index('Date')
        df = df.sort_index()
        split_date = pd.Timestamp('05-01-2017')
        df = df.loc[:split_date]
        X = p.iloc[:, [0, 2]].values
        Y = q.iloc[:, [0, 1]].values
        wcss = []
        for i in range(1, 11):
            kmean = KMeans(n_clusters=i, init="k-means++", n_init=10, max_iter=300)
            kmean.fit(X)
            wcss.append(kmean.inertia_)
        kmean = KMeans(n_clusters=3, init="k-means++", max_iter=300, n_init=10)
        y_kmeans = kmean.fit_predict(X)
        kmean1 = KMeans(n_clusters=3, init="k-means++", max_iter=300, n_init=10)
        y_kmeans1 = kmean.fit_predict(Y)
        pickle.dump(kmean,open('models/model1.pkl','wb'))
        q['cluster_value']=y_kmeans1
        json_records = q.to_json(orient='records')
        print(type(json_records))
        data = json.loads(json_records)
        print(data)
        Database.insert_many('Recommendation', data)
        model = pickle.load(open('models/model1.pkl','rb'))
        model.fit_predict(X)

    @staticmethod
    def time_series():
        pass