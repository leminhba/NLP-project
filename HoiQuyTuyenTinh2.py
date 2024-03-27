import numpy as np 
import tensorflow as tf 
import matplotlib.pyplot as plt 
np.random.seed(101) 
tf.random.set_seed(101)
# Genrating random linear data 
# There will be 50 data points ranging from 0 to 50 
x = np.linspace(0, 50, 50) 
y = np.linspace(0, 50, 50) 
  
# Adding noise to the random linear data 
x += np.random.uniform(-4, 4, 50) 
y += np.random.uniform(-4, 4, 50) 
  
n = len(x) # Lấy số lượng mẫu huấn luyện, ap dung cho mang 1 chieu
#n_samples = x.shape[0] # Lấy số lượng mẫu huấn luyện, ap dung cho mang nhieu chieu
# Plot of Training Data 
plt.scatter(x, y) 
plt.xlabel('x') 
plt.xlabel('y') 
plt.title("Training Data") 
# plt.show()
tf.compat.v1.disable_eager_execution()
# tạo hai cái thùng rỗng sử dụng tf.placeholder trong đó X là dữ liệu và Y là nhãn của dữ liệu. Lát nữa sẽ truyền vào x và y tương ứng trong session.
X = tf.compat.v1.placeholder(tf.float32) 
Y = tf.compat.v1.placeholder(tf.float32) 
W = tf.Variable(np.random.randn(), name = "W") 
b = tf.Variable(np.random.randn(), name = "b") 

learning_rate = 0.01
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