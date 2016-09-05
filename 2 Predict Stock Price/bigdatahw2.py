__author__ = 'jingyiyuan'

from yahoo_finance import Share
import datetime
import numpy as np
import pandas as pd
import sklearn

from pandas.io.data import DataReader
from sklearn import linear_model


def create_lagged_series(symbol, start_date, end_date):
    """This calculates the returns from the start_data to the end_data"""

    # Obtain stock information from Yahoo Finance

    #print "here"
    ts = DataReader(symbol, "yahoo", start_date, end_date)
    tslag = pd.DataFrame(index=ts.index)
    tslag["Open"] = ts["Open"]
    #print tslag["Open"]#Name: Open, dtype: float64
    returns = []
    n = len(tslag["Open"])
    for i in range(n - 1):
        ret_temp = (tslag["Open"][i + 1] - tslag["Open"][i])/tslag["Open"][i] * 100.
        returns.append(ret_temp)
    #print returns, "this is returns"
    price = tslag["Open"][n - 1]
    return returns,price

if __name__ == "__main__":
    res = []
    prices = []
    predicted_returns = []#percentage
    companies = ["BAC", "C", "IBM", "AAPL", "GE", "T", "MCD", "NKE", "TWTR", "TSLA"]
    for i in range(len(companies)):
        share = companies[i]
        returns = create_lagged_series(share, datetime.datetime(2016,1,1), datetime.datetime(2016,3,10))[0]
        price = create_lagged_series(share, datetime.datetime(2016,1,1), datetime.datetime(2016,3,10))[1]
        n = len(returns)#46
        #then calculates 1 day lagged returns, 3 days lagged returns and 1 week lagged returns
        lags = [2,3,4,5,6,7]
        size = len(returns[6:(n - 1)])#39
        X_train = returns[6:(n - 1)] # lag = 1
        for t in range(len(lags)):
            temp = returns[(7 - lags[t]):(n - lags[t])]
            X_train = X_train + temp
        X_train = np.asarray(X_train).astype(float)
        X_train = X_train.reshape(7, size)
        X_train = X_train.T

        # Use the prior 1 day of returns as predictor values, with direction as the response
        y_train = np.asarray(returns[0:size]).astype(float)
        if (i == 0):
            print X_train
            print y_train

        # predict returns 03/09
        # create and fit the three models
        X_test = [returns[n - 1],returns[n - 2],returns[n - 3],returns[n - 4],returns[n - 5],returns[n - 6],returns[n - 7]]
        #X_test = [returns[n - 1],returns[n - 3],returns[n - 7]]
        models = [linear_model.LinearRegression(), linear_model.Ridge(alpha = .1), linear_model.Lasso(alpha = 0.1)]#all for classification but the model is regression

        LR = linear_model.Ridge(alpha = 0.1)
        LR.fit (X_train, y_train)
        #print "linear regression coeffients:",LR.coef_
        res1 = LR.predict(X_test)[0]

        ridge = linear_model.Ridge(alpha = 0.1)
        ridge.fit (X_train, y_train)
        #print "ridge coeffients:",ridge.coef_
        res2 = ridge.predict(X_test)[0]

        lasso = linear_model.Lasso(alpha = 0.05)
        lasso.fit (X_train, y_train)
        #print "lasso coeffients:",lasso.coef_
        res3 = lasso.predict(X_test)[0]

        res_return = (res1 + res2 + res3)/6
        prices.append(price)
        res_this = price* (100. + res_return)/100.
        predicted_returns.append(res_return)
        res.append(res_this)

    print prices,"prices"
    print predicted_returns
    print res


