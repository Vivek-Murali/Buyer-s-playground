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
from sklearn.ensemble.forest import RandomForestRegressor
from bokeh.models import HoverTool,FactorRange, Plot, LinearAxis, Grid
from bokeh.plotting import figure
from bokeh.io import output_file,save
import bokeh.plotting
from bson.objectid import ObjectId
from bokeh.models import DatetimeTickFormatter
from math import pi
from bokeh.embed import components
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
        a = db.ratings.find()
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
        a = db.test2.find()
        df = pd.DataFrame(list(a))
        df['Arrival Date'] = pd.to_datetime(df['Arrival Date'])
        df = df.set_index('Arrival Date')
        split_date = pd.Timestamp('01-09-2018')
        df.sort_index(inplace=True)
        df = df.loc[df['Commodity Value'] == 154]
        df.drop(['Arrivals (Tonnes)', ''], axis=1, inplace=True)
        train = df.loc[:split_date]
        test = df.loc[split_date:]
        train = train.iloc[:, [0, 3, 4, 5]]
        test = test.iloc[:, [0, 3, 4, 5]]
        X_train = train.iloc[:, :-1].values
        X_test = test.iloc[:, :-1].values
        y_train = train.iloc[:, 3].values
        y_test = test.iloc[:, 3].values
        RF_Model = RandomForestRegressor(n_estimators=100,
                                         max_features=1, oob_score=True)
        RGR = RF_Model.fit(X_train, y_train)
        y_pred2 = RGR.predict(X_test)
        y_pred2df = pd.DataFrame(data=y_pred2, columns=['Predected Values'])
        y_pred2df = y_pred2df.head(10)
        print(y_pred2df)
        source1 = bokeh.plotting.ColumnDataSource(
            data={'y': y_pred2df['Predected Values']})
        TOOLTIPS = [
            ('Forcasted Price', "@y"),
        ]
        hover = HoverTool(
            tooltips=TOOLTIPS,
        )
        p = figure(y_axis_label='price', x_axis_label='days', plot_width=1200, plot_height=200)
        p.add_tools(hover)
        x = [1,2,3,4,5,6,7,8,9,10]
        y = y_pred2df['Predected Values']
        p.line(x,y)
        output_file('templates/prechart.html')
        save(p)
        pickle.dump(RF_Model, open('model2.pkl','wb'))
        model = pickle.load(open('model2.pkl','rb'))