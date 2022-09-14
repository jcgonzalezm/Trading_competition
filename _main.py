# -*- coding: utf-8 -*-
"""
Created on Wed Feb  9 10:19:15 2022

@author: JOSECG1
"""
from getstockdata import stock_data, feeder
from Executor import ticker
from animation import animated_graph
from portfolio import trader
from model import NEAT

import os
import configparser

class run(object):
    
    def __init__(self,NEAT_config_file , operations_config_file):
        
        self.parse_config(operations_config_file)
        
        self.getData(self.stock , self.key , self.shortdataby)
        self.data_feeder = feeder(self.complete_data,self.indicators_to_use) #set the iterator
        self.animation = animated_graph(self.data_feeder)
        
        self.neat_model = NEAT(NEAT_config_file)
        
        execution = self.neat_model.p.run(self.start_run, 2)
        print("execution" , execution)
        # print('\nBest genome:\n{!s}'.format(winner))
        
    def parse_config(self, operations_config_file):
        config = configparser.ConfigParser()
        config.read(operations_config_file)
        
        try:
            self.stock = config['DEFAULT']['stock']
            self.key = config['DEFAULT']['key']
            self.shortdataby = config['DEFAULT']['shortdataby']
            self.number_of_genomes = config['MODEL']['number_of_genomes']
        except KeyError as e: 
            print(f"CRITICAL: No {e} found on operations_config_file")        
        
        
            
    def start_run(self, genomes, config):
        print('enters run')
        
        self.neat_model.eval_genomes(genomes, config)
        
        # while len(self.traders)>0 : 
        self.runs = 0
        while len(self.neat_model.traders)>0: 
            print('self.runs',self.runs)
            self.animation.setup()
        
            self.data_feeder = feeder(self.complete_data,self.indicators_to_use) #reset iterator for the Ticker
            nets_traders_ge = (self.neat_model.nets , self.neat_model.traders , self.neat_model.ge)
            
            
            
            self.ticker = ticker(data_feeder = self.data_feeder ,
                                 animation = self.animation , 
                                 nets_traders_ge=nets_traders_ge)
        
            self.neat_model.nets , self.neat_model.traders , self.neat_model.ge = self.ticker.nets_traders_ge
            
            
            
            self.neat_model.kill_lowest_fitness()
            self.runs += 1
            
        print('exit start_run')
        print('len(self.traders)', len(self.neat_model.traders))
        
        #check values after Ticker ended
            

    def getData(self, stock , key, shortdataby=False):

        self.complete_data = stock_data(stock , key, shortdataby=shortdataby)
        # self.self.complete_data = stock_data('SPY' , 'QXDW7T3QI0W3B9N5')
        self.complete_data.calculate_RSI(periods=9)
        self.complete_data.calculate_RSI(periods=14)
        self.complete_data.calculate_RSI(periods=28) #will not be used
        self.complete_data.calculate_MACD(short_window=12, long_window=24, triger_line_days=9)
        self.complete_data.calculate_MACD(short_window=24, long_window=84, triger_line_days=18)
        
        #TODO
        self.complete_data.data = self.complete_data.data.reset_index() 
        for i in self.complete_data.indicators:
            for e in self.complete_data.indicators[i]:
                self.complete_data.indicators[i][e] = self.complete_data.indicators[i][e].reset_index()
                self.complete_data.indicators[i][e] = self.complete_data.indicators[i][e].drop(['index'], axis=1)
                
        self.complete_data.data = self.complete_data.data[['close']]
        #TODO
        
        # indicators_to_use = {}
        # indicators_to_use = {'RSI': [9,14]}
        # indicators_to_use = {'RSI': [9,14],'MACD': ['12_24_9','24_84_18']}
        self.indicators_to_use = {'RSI': [9],'MACD': ['12_24_9']}
        self.data_feeder = feeder(self.complete_data,self.indicators_to_use) #defines an iterator for the stock and indicators movements
#----------------------------------------------------------------------------------------



if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.

    local_dir = os.path.dirname(__file__)
    NEAT_config_path = os.path.join(local_dir, 'mod_config-feedforward.txt')
    operation_config_path = os.path.join(local_dir, 'operations_config_file.txt')
    mymodel = run(NEAT_config_path , operation_config_path)
    
