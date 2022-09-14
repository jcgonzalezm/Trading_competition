# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 09:29:43 2022

@author: JOSECG1
"""
import pandas as pd
import numpy as np

import pickle
import random
import matplotlib.pyplot as plt
import time

from datetime import datetime

from portfolio import trader
from animation import animated_graph


class ticker():
    
    def __init__(self, data_feeder , animation , nets_traders_ge):
        
        print('enters_ticker')
        
        self.nets_traders_ge = nets_traders_ge
        self.nets , self.traders , self.ge = self.nets_traders_ge
        self.animation = animation
        
        self.iterator = data_feeder.iterator

        self.execution_in_progress = True
        while self.execution_in_progress:
            if not self.execution_in_progress: break
            self.tick()
        
    def tick(self):
        
        def end_procedure(reason):
            print('exit_procedure --- ' + reason)
            self.execution_in_progress = False
            self.nets_traders_ge = (self.nets , self.traders , self.ge)
            pass

        if len(self.traders) == 0:
            end_procedure('due to self.traders == 0')

        try:
            self.tick_position, self.tick_data = next(self.iterator)
            self.execution_in_progress = True
            
            self.animation.step(self.tick_position,self.tick_data)
                
            for x, trader_ind in enumerate(self.traders):  
                
                output = self.nets[self.traders.index(trader_ind)].activate((self.tick_data['close'], 
                                                                         self.tick_data['rsi_close_9']))
    
                if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                    trader_ind.buy(1 , self.tick_data['close'])
                    
                trader_ind.current_status(self.tick_data['close'])
                self.ge[x].fitness = trader_ind.total_profit_losses
                            
                if trader_ind.available_amount<0 or \
                    trader_ind.total_profit_losses<-500:
                        
                    print('trader_kill' , x)
                    self.ge[self.traders.index(trader_ind)].fitness -= 10000
                    self.nets.pop(self.traders.index(trader_ind))
                    self.ge.pop(self.traders.index(trader_ind))
                    self.traders.pop(self.traders.index(trader_ind))            

        except StopIteration: 
            end_procedure('due to end of iterator')

            


            

        
            


      
      
