# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 11:40:54 2021

@author: James Ang
"""

import numpy as np
from sklearn.linear_model import LinearRegression

x = np.array([5, 15, 25, 35, 45, 55]).reshape((-1, 1))
# x = np.array([1, 2, 3, 4, 5, 6]).reshape((-1, 1))
y = np.array([5, 20, 14, 32, 22, 38])

print(x)

print(y)

model = LinearRegression()
model.fit(x, y)

# model = LinearRegression().fit(x, y)
y_pred = model.predict(x)
print(y_pred)

np.diff(y_pred)
