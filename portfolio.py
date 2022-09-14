# -*- coding: utf-8 -*-
"""
portafolio.py
- It creates the trader obj which is the primarly 'executor' of tradgin actions.
    The model will be evaluated the behaviour of the survival traders across several generations.
"""
import pandas as pd
from datetime import datetime

class trader(object):
    '''
    The trader obj represents an actual 'contestant' trader which buys, sells and hold based on his own expertise
    '''
    
    def __init__(self, trader_id):
        self.trader_id = trader_id
        # self.initial_amount = initial_amount
        # self.available_amount = self.initial_amount #minus positions open
        self.total_profit_losses= 0
        
        self.position = pd.DataFrame(columns=['quantity','price'])
        self.parameters_to_avoid_compare =  ['position','compare_amount','compare_perc','parameters_to_avoid_compare']
        # self.current_status()
        
    def define_initial_amount(self , initial_amount):
        self.initial_amount = initial_amount
        self.available_amount = self.initial_amount #minus positions open
        self.total_profit_losses = 0
        self.on_run_total_profit_losses = 0
        self.position = pd.DataFrame(columns=['quantity','price'])
        
        
        
    def buy(self, quantity, price):
                
        total_amount = quantity * price
        result = False
        if self.available_amount >= total_amount:
                
            to_add = {'quantity': -quantity,'price' : price}
            self.position = self.position.append(to_add, ignore_index=True)
            # self.available_amount = self.available_amount - (quantity*price) #extract from our account
            self.available_amount = 0 #extract from our account
            
            result = True
        
        return result
    
    def sell(self, quantity, price):
        
        #check if I have the requiered amount of positions opened.
        current_position_on_stock = -self.position['quantity'].sum()
        result = False
        if quantity > current_position_on_stock:
            # print('not enough positions to sell')
            pass
        else:
            #TODO
            to_sell = {'quantity': quantity,'price' : price}
            self.position = pd.DataFrame(columns=['quantity','price'])
            result = True
        
        return result

            
    def current_status(self, current_price , log_result=False):
        
        self.current_open_position = sum(-self.position['quantity'] * current_price)
        self.general_invested_position = sum(-self.position['quantity'] * self.position['price'])
        self.on_run_total_profit_losses = self.current_open_position - self.general_invested_position
                                            
        self.total_quantity = self.position['quantity'].sum()
        try:
            self.average_price = self.on_run_total_profit_losses / (-self.total_quantity)
        except: self.average_price = 0
        
        self.quantity_of_buys  = self.position['quantity'][self.position['quantity']<0].count()
        self.quantity_of_sells  = self.position['quantity'][self.position['quantity']>0].count()
        self.quantity_of_breath  = self.quantity_of_buys + self.quantity_of_sells
        
        return self.sell(1,current_price)
        
        
    def compare_against(self, portfolio):
        
        self.compare_amount = {'parameter': '(local_port, external_port, compartive)'}
        self.compare_perc = {}
        
        for parameter in self.__dict__.keys(): #list of parameters created in here
            if parameter in self.parameters_to_avoid_compare: continue
        
            local_parameter = getattr(self, parameter)
            external_parameter = getattr(portfolio, parameter)

            if local_parameter or external_parameter:
                self.compare_amount[parameter] = local_parameter, external_parameter, local_parameter - external_parameter
                self.compare_perc[parameter] = local_parameter, external_parameter, (local_parameter/external_parameter)-1
                
    def get_total_profit_losses(self):
        self.total_profit_losses = self.total_profit_losses + self.on_run_total_profit_losses
        
    
    def clear_positions(self, price):
        self.position = pd.DataFrame(columns=['quantity','price'])