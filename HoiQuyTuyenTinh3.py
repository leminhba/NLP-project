import numpy as np 
import pyodbc 
import tensorflow as tf 
import matplotlib.pyplot as plt 

conn = pyodbc.connect('Driver={SQL Server};Server=.;Database=GSDGNganh;Trusted_Connection=yes;')
cursor = conn.cursor()
cursor.execute('SELECT Rd_ivalue,Rd_Year FROM  ReportData WHERE (Rd_Area_Id=1) And (Rd_Indicator_Id = 836) And  (Rd_Year < 2020) AND (Rd_Year > 2010) ORDER BY Rd_Year')
results = cursor.fetchall()
results_as_list = [i[0] for i in results]

#x = np.asarray([3, 4, 5, 6, 6, 4, 90, 60, 7])
x = np.fromiter(results_as_list, dtype=np.int64)

cursor2 = conn.cursor()
cursor2.execute('SELECT Rd_ivalue,Rd_Year FROM  ReportData WHERE (Rd_Area_Id=1) And (Rd_Indicator_Id = 707) And  (Rd_Year < 2020) AND (Rd_Year > 2010) ORDER BY Rd_Year')
results2 = cursor2.fetchall()
results_as_list2 = [i[0] for i in results2]

y = np.fromiter(results_as_list2, dtype=np.int64)
#y = np.asarray([1, 2, 2, 3, 1, 1, 30, 20, 2])
n = len(x) # Number of data points 
# Plot of Training Data 
plt.scatter(x, y) 
plt.xlabel('x') 
plt.xlabel('y') 
plt.title("Training Data") 
plt.show()
tf.compat.v1.disable_eager_execution()
X = tf.compat.v1.placeholder(tf.float32) 
Y = tf.compat.v1.placeholder(tf.float32) 
W = tf.compat.v1.get_variable('weights', initializer=tf.constant(0.0))
b = tf.compat.v1.get_variable('bias', initializer=tf.constant(0.0))

learning_rate = 0.00000000001 # dieu chinh gia tri nay theo gia tri dau vao lon hay be de khong bi NAN
training_epochs = 1000
#  model dự đoán như sau
y_pred = tf.add(tf.multiply(X, W), b) 
  
# Mean Squared Error Cost Function
cost = tf.reduce_sum(tf.pow(y_pred-Y, 2)) / (2 * n)
  
# Gradient Descent Optimizer
optimizer = tf.compat.v1.train.GradientDescentOptimizer(learning_rate).minimize(cost)
  
# Global Variables Initializer 
init = tf.compat.v1.global_variables_initializer()
# Starting the Tensorflow Session 
with tf.compat.v1.Session() as sess: 
      
    # Initializing the Variables 
    sess.run(init) 
      
    # Iterating through all the epochs 
    for epoch in range(training_epochs): 
          
        # Feeding each data point into the optimizer using Feed Dictionary 
        for (_x, _y) in zip(x, y): 
            sess.run(optimizer, feed_dict = {X : _x, Y : _y}) 
          
        # Displaying the result after every 50 epochs 
        if (epoch + 1) % 50 == 0: 
            # Calculating the cost a every epoch 
            c = sess.run(cost, feed_dict = {X : x, Y : y}) 
            print("Epoch", (epoch + 1), ": cost =", c, "W =", sess.run(W), "b =", sess.run(b)) 
      
    # Storing necessary values to be used outside the Session 
    training_cost = sess.run(cost, feed_dict ={X: x, Y: y}) 
    weight = sess.run(W) 
    bias = sess.run(b) 