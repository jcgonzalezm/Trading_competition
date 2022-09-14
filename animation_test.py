# # # -*- coding: utf-8 -*-
# # """
# # Created on Sat Feb  5 18:12:03 2022

# # @author: JOSECG1
# # """

# import matplotlib.pyplot as plt
# import numpy as np
# from datetime import datetime


# def update_title(axes):
#     axes.set_title(datetime.now())
#     axes.figure.canvas.draw()

# fig, ax = plt.subplots()

# # x = np.linspace(-3, 3)
# x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
# y = np.array([1, 1, 2, 2, 3, 3, 4, 5, 5])
# t1 = np.array([np.nan, 2, 3, np.nan, 5, np.nan ,7 ,np.nan, np.nan])
# t2 = np.array([np.nan, 2, 3, np.nan, 5, np.nan ,7 ,np.nan, np.nan])


# tt = []
# for n in range(0,len(t1)):
#     t_pos = []
#     for i,trader_number in enumerate([t1,t2]):
#         if not np.isnan(trader_number[n]):
#             t_pos.append(i)
#     if not t_pos: t_pos.append(np.nan)
#     tt.append(t_pos)
    

# # x2 = np.array([np.nan, 2, 3, np.nan, 5, np.nan ,7 ,np.nan, np.nan])
# ax.plot(x, y)
# # ax.plot(x, x2, marker ='^', color='g', ms = 20)

# for text, x , y in zip(tt, x , y):
#     print(text , x , y)
#     array_sum = np.sum(text)
#     if not np.isnan(array_sum):

#         plt.text(x, y, str(text), color="red", fontsize=12, bbox={
#             'facecolor': 'white', 'alpha': 0.5, 'pad': 5})

# plt.show()

import numpy as np
import matplotlib.pyplot as plt
# x = np.arange(0, 10, 0.1)
# y1 = 0.05 * x**2
# y2 = -1 *y1

# fig, ax1 = plt.subplots()

# ax2 = ax1.twinx()
# ax1.plot(x, y1, 'g-')
# ax2.plot(x, y2, 'b-')

# ax1.set_xlabel('X data')
# ax1.set_ylabel('Y1 data', color='g')
# ax2.set_ylabel('Y2 data', color='b')

# plt.show()

x = [np.nan, 1165, 1166]
y1 = [np.nan, 7, 7]
fig, ax1 = plt.subplots()
ax1.plot(x, y1, 'g-')

plt.show()