# (1) Model Identification. Use plots and summary statistics to identify trends, seasonality, and autoregression elements to get an idea of the amount of differencing and the size of the lag that will be required.(2) Parameter Estimation. Use a fitting procedure to find the coefficients of the regression model. (3) Model Checking. Use plots and statistical tests of the residual errors to determine the amount and type of temporal structure not captured by the model.
from datetime import datetime
import numpy as np 
import pandas as pd
from pandas import read_csv
from pandas import DataFrame
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from matplotlib import pyplot
from pandas.plotting import autocorrelation_plot
from sklearn.metrics import mean_squared_error
from math import sqrt
# load dataset
def parser(x):
	return datetime.strptime('190'+x, '%Y-%m')
#dataframe
#Dữ liệu chuỗi thời gian là stationary nếu chúng không có thêm trend và seasonal. Các đặc tính thống kê trên chuỗi thời gian là nhất quán theo thời gian ví dụ như mean và variance. Khi dữ liệu chuỗi thời gian ở dạng stationary thì chúng có thể dễ dàng mô hình hóa với độ chính xác cao hơn.
series = read_csv('shampoo.csv', header=0, index_col=0, parse_dates=True, squeeze=True, date_parser=parser)
series.index = series.index.to_period('M')
#autocorrelation_plot(series)
#pyplot.show()
#df_log = np.log(df)

def adfuller_test(sales):
    result=adfuller(sales)
    labels = ['ADF Test Statistic','p-value','#Lags Used','Number of Observations']
    for value,label in zip(result,labels):
        print(label+' : '+str(value) )
    if result[1] <= 0.05:
         print("strong evidence against the null hypothesis(Ho), reject the null hypothesis. Data is stationary")
    else:
        print("weak evidence against null hypothesis,indicating it is non-stationary ")

adfuller_test(series.values)
# fit model
#This sets the lag value to 5 for autoregression, uses a difference order of 1 to make the time series stationary, and uses a moving average model of 0.
# split into train and test sets
X = series.values
size = int(len(X) * 0.66)
train, test = X[0:size], X[size:len(X)]
history = [x for x in train]
predictions = list()
# walk-forward validation
for t in range(len(test)):
	model = ARIMA(history, order=(5,1,0))
	model_fit = model.fit()
	output = model_fit.forecast()
	yhat = output[0]
	predictions.append(yhat)
	obs = test[t]
	history.append(obs)
	print('predicted=%f, expected=%f' % (yhat, obs))
# evaluate forecasts
rmse = sqrt(mean_squared_error(test, predictions))
print('Test RMSE: %.3f' % rmse)
# plot forecasts against actual outcomes
pyplot.plot(test)
pyplot.plot(predictions, color='red')
pyplot.show()
#model = ARIMA(series, order=(5,1,0))

#model = ARIMA(df['Rd_ivalue'], order=(1,1,1))
model_fit = model.fit()
# summary of fit model
print(model_fit.summary())
# line plot of residuals
residuals = DataFrame(model_fit.resid)
residuals.plot()
#pyplot.show()
# density plot of residuals
residuals.plot(kind='kde')
#pyplot.show()
# summary stats of residuals
#print(residuals.describe())