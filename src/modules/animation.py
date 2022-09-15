# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 11:09:03 2022
"""
#importing libraries
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
import math
from modules import portfolio

import pandas as pd
import numpy as np
import neat


class animated_graph(object):
    
    def __init__(self):
        
        # self.df = feeder.data
        # self.df.index = pd.to_datetime(self.df.index)
        # self.myiter = feeder.iterator
        self.colors = ('b','g','r','c','m','y','k','b','g','r','c','m','y','k') #TODO
        
        self.fig = plt.figure(figsize=(10, 6))

    def define_how_many_subplots(self, number_of_grahs , columns_wanted):            

        rows = math.ceil(number_of_grahs / columns_wanted) 
        
        if ((number_of_grahs-1) % columns_wanted) != 0 :
            rows += 1
            
        return rows,columns_wanted        
        
  
    def setup(self, feeder, tittle, n_traders):
        
        plt.clf()
        
        self.df = feeder.data
        self.df.index = pd.to_datetime(self.df.index)
        self.myiter = feeder.iterator
        
        self.fig.suptitle(tittle)
        self.fig_text = self.fig.text(0.35, 0.6, 'number of traders alive - ' + str(n_traders), fontsize = 15)
        self.ax = {}
        self.continues_time = []
        self.continues_values = {}
        for _,col in enumerate(self.df.columns.values):
            self.continues_values[col] = []
        
        # print('enters_setup')
        rows_wanted,columns_wanted = self.define_how_many_subplots(len(self.continues_values.keys()), 4)
        # self.n = 0

        for color, column in enumerate(self.continues_values.keys()):
            
            if column == 'close':
                self.ax[column] = plt.subplot(rows_wanted, columns_wanted, (1,columns_wanted), frameon=True)
                self.ax['buys'] = self.ax[column].twinx()
                self.ax['buys'].set_ylim(0,20)
            else:
                self.ax[column] = plt.subplot(rows_wanted, columns_wanted, int(color+columns_wanted), frameon=True, sharex=self.ax['close'])
            
            column_min = self.df[column].min()
            column_max = self.df[column].max()
            
            if not(pd.isnull(column_min) or pd.isnull(column_max)): #neither are nan
                self.ax[column].set_ylim(column_min, column_max)    
                
            # self.ax[column].set_xlim('2021-09-16', '2021-11-09')
            self.ax[column].set_xlim(feeder.botton_random_window , feeder.upper_random_window)            
            self.ax[column].set_title(column)
            self.ax[column].plot(self.continues_time,
                                self.continues_values[column],
                                color=self.colors[int(color-1)], label = column)
            
        return self.ax
    
    def step(self, tick_position , tick_data , n_traders , traders_bought):
            
        self.continues_time.append(tick_position)
        
        self.fig_text.set_visible(False)
        self.fig_text = self.fig.text(0.35, 0.6, 'number of traders alive - ' + str(n_traders), fontsize = 15)
        
        # self.continues_time.append(i[0])
        # self.continues_time.append(datetime.fromisoformat(i[0]))
        # print("traders_bought")
        # print(traders_bought[-1])
        
        self.ax['buys'].plot(self.continues_time, traders_bought, linestyle = '--', color='k')
        
        data = dict(tick_data)
        for values in data.keys():
            self.continues_values[values].append(data[values])

        for color, column in enumerate(self.continues_values.keys()):   
            self.ax[column].plot(self.continues_time,
                                 self.continues_values[column], 
                                 color=self.colors[color])
            
        plt.pause(0.0000001)
        
            
        return self.ax
        
    # def run(self):
    #     self.anim = animation.FuncAnimation(self.fig, self.step, init_func=self.setup,
    #                                    frames=self.myiter, 
    #                                    interval=100, blit=False, repeat=False)      
    
    

