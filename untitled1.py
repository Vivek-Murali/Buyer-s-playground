#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 00:15:32 2019

@author: jetfire
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.tseries.offsets import MonthEnd
from keras.callbacks import EarlyStopping
from keras.layers import Dense
from keras.models import Sequential
import keras.backend as K
from sklearn.preprocessing import MinMaxScaler
from keras.layers import LSTM

#Initilaing Scaler to scale the values for the modle values
sc = MinMaxScaler()
#data preprocessing
df  = pd.read_csv("Apple_year_data.csv")
df.drop(['Unnamed: 0'], axis=1, inplace=True)
df['Arrival Date'] = pd.to_datetime(df['Arrival Date'])
df = df.set_index('Arrival Date')
split_date = pd.Timestamp('01-09-2018')
train = df.loc[:split_date, ['Modal Price(Rs./Quintal)']]
test = df.loc[split_date:, ['Modal Price(Rs./Quintal)']]
train_sc = sc.fit_transform(train)
test_sc = sc.transform(test)
X_train  = train_sc[:-1]
y_train = train_sc[1:]
X_test = test_sc[:-1]
y_test = test_sc[1:]


K.clear_session()
#Modeling of the fully connected predectors
model = Sequential()
model.add(Dense(24, input_dim = 1, activation='relu'))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam')
model.summary()
early_stop = EarlyStopping(monitor='loss', patience=10,verbose=10)
model.fit(X_train,y_train,epochs=200,batch_size=2,verbose=1,callbacks=[early_stop])

y_pred = model.predict(X_test)
plt.plot(y_test)
plt.plot(y_pred)
#MOdeling of Recurent Predictor
'''X_train.shape
X_train[:,None].shape
X_train_t = X_train[:,None]
X_test_t = X_test[:,None]
K.clear_session()
model = Sequential()
model.add(LSTM(6, input_shape=(1,1)))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(X_train_t,y_train,epochs=200,batch_size=2,verbose=1,callbacks=[early_stop])
y_pred = model.predict(X_test_t)
plt.plot(y_test)
plt.plot(y_pred)

#windows
train_sc_df = pd.DataFrame(train_sc,columns=['Scaled'],index=train.index)
test_sc_df = pd.DataFrame(test_sc,columns=['Scaled'],index=test.index)
for s in range(1,32):
    train_sc_df['shift_{}'.format(s)] = train_sc_df['Scaled'].shift(s)
    test_sc_df['shift_{}'.format(s)] = test_sc_df['Scaled'].shift(s)
    
X_train = train_sc_df.dropna().drop('Scaled', axis=1)
y_train = train_sc_df.dropna()[['Scaled']]
X_test = test_sc_df.dropna().drop('Scaled',axis=1)
y_test = test_sc_df.dropna()[['Scaled']]   

X_train = X_train.values
X_test = X_test.values
y_train = y_train.values
y_test = y_test.values

model = Sequential()
model.add(Dense(31, input_dim = 31, activation='relu'))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam')
model.summary()
model.fit(X_train,y_train,epochs=200,batch_size=2,verbose=1,callbacks=[early_stop])
y_pred = model.predict(X_test)
plt.plot(y_test)
plt.plot(y_pred)    

X_train_t = X_train.reshape(X_train.shape[0],1,31)
X_test_t = X_test.reshape(X_test.shape[0],1,31)
K.clear_session()
model = Sequential()
model.add(LSTM(6, input_shape=(1,31)))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(X_train_t,y_train,epochs=200,batch_size=2,verbose=1,callbacks=[early_stop])
y_pred = model.predict(X_test_t)
plt.plot(y_test)
plt.plot(y_pred)


#test

X_train_t = X_train.reshape(X_train.shape[0],31,1)
X_test_t = X_test.reshape(X_test.shape[0],31,1)
K.clear_session()
model = Sequential()
model.add(LSTM(6, input_shape=(31,1)))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(X_train_t,y_train,epochs=600,batch_size=65,verbose=1)
y_pred = model.predict(X_test_t)
plt.plot(y_test)
plt.plot(y_pred)
'''