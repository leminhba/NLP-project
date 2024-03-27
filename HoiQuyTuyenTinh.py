import numpy as np 
import pyodbc 
from sklearn import datasets, linear_model
import matplotlib.pyplot as plt 

conn = pyodbc.connect('Driver={SQL Server};Server=.;Database=GSDGNganh;Trusted_Connection=yes;')
cursor = conn.cursor()
cursor.execute('SELECT Rd_ivalue,Rd_Year FROM  ReportData WHERE (Rd_Area_Id=1) And (Rd_Indicator_Id = 836) And  (Rd_Year < 2020) AND (Rd_Year > 2010) ORDER BY Rd_Year')
results = cursor.fetchall()
results_as_list = [i[0] for i in results]


x = np.fromiter(results_as_list, dtype=np.int64)
X = np.array([x]).T
cursor2 = conn.cursor()
cursor2.execute('SELECT Rd_ivalue,Rd_Year FROM  ReportData WHERE (Rd_Area_Id=1) And (Rd_Indicator_Id = 707) And  (Rd_Year < 2020) AND (Rd_Year > 2010) ORDER BY Rd_Year')
results2 = cursor2.fetchall()
results_as_list2 = [i[0] for i in results2]

#y = np.fromiter(results_as_list2, dtype=np.int64)

y = np.array([np.fromiter(results_as_list2, dtype=np.int64)]).T


def Convert(n):   
    # Building Xbar 
    one = np.ones((n.shape[0], 1))  
    return np.concatenate((one, n), axis = 1)

#y1 = w_1*155 + w_0
Xbar = Convert(X)
# fit the model by Linear Regression
regr = linear_model.LinearRegression(fit_intercept=False) # fit_intercept = False for calculating the bias
regr.fit(Xbar, y)
r_sq = regr.score(Xbar, y)
# Compare two results
print( 'Solution found by scikit-learn  : ', regr.coef_ )
Test =  Convert(np.array([[950000]]).T)
print( 'Predic  : ',regr.predict(Test))
# Drawing the fitting line 
plt.plot(X.T, y.T, 'ro')     # data 
plt.plot(Xbar, regr.predict(Xbar)) 
plt.show()