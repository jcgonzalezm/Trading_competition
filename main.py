# -*- coding: utf-8 -*-
"""
Main.py
 - This .py its the entry point of contact for the overall process. From all the modules and process are started.
"""
from getstockdata import stock_data, feeder
from animation import animated_graph
from model import NEAT

import os
import configparser
import pandas as pd
import numpy as np

class run(object):
    
    def __init__(self,NEAT_config_file , operations_config_file):
        
        self.parse_config(operations_config_file)
        
        self.getData(self.stock , self.key , self.shortdataby)
        self.data_feeder = feeder(self.complete_data,self.indicators_to_use) #set the iterator
        self.animation = animated_graph()
        self.neat_model = NEAT(NEAT_config_file)
        
        self.writer = pd.ExcelWriter('outputs/output.xlsx')
        self.sheet_name = 1
        
        execution = self.neat_model.p.run(self.eval_genomes, self.number_of_genomes)
        print("execution" , execution)
        self.writer.save()
        
        # print('\nBest genome:\n{!s}'.format(winner))
        
    def parse_config(self, operations_config_file):
        config = configparser.ConfigParser()
        config.read(operations_config_file)
        
        try:
            self.stock = config['DEFAULT']['stock']
            self.key = config['DEFAULT']['key']
            self.shortdataby = config['DEFAULT']['shortdataby']
            self.display_graph = int(config['DEFAULT']['display_graph'])
            self.traders_initial_amount_multiplier = float(config['DEFAULT']['traders_initial_amount_multiplier'])
            self.target_profit = float(config['DEFAULT']['target_profit'])
            
            self.number_of_genomes = int(config['MODEL']['number_of_genomes'])
            
        except KeyError as e: 
            print(f"CRITICAL: No {e} found on operations_config_file")        
        
            
    def eval_genomes(self, genomes, config):
        print('enters run')
        
        self.neat_model.set_genomes(genomes, config)
        
        self.stock_data_runs = 0
        while len(self.neat_model.traders)>0:
            #From here we start a new cicle of stock analysis
            print('self.stock_data_runs',self.stock_data_runs)
            
            self.data_feeder = feeder(self.complete_data,self.indicators_to_use) #reset iterator for the Ticker
            traders_initial_amount = int(self.data_feeder.current_step[1]['close'] * self.traders_initial_amount_multiplier)
            self.neat_model.define_traders_parameters(traders_initial_amount = traders_initial_amount,
                                                      target_profit = self.target_profit)
            
            if self.display_graph:
                tittle_fig = str('stock_data_runs - '  + str(self.stock_data_runs) + ' // gen - ')
                self.animation.setup(feeder = self.data_feeder,
                                     tittle = tittle_fig , 
                                     n_traders=len(self.neat_model.traders))

            self.execution_in_progress = True
            while self.execution_in_progress:
                if not self.execution_in_progress: break
                self.tick()
                
            
            self.neat_model.report_positions()
            self.report()
                            
            self.neat_model.kill_lowest_fitness()
            self.stock_data_runs += 1
            
            input('stop')
            
        print('exit start_run')
        
    def tick(self):
        
        def end_procedure(reason):
            print('exit_procedure --- ' + reason)
            self.execution_in_progress = False
            pass

        if len(self.neat_model.traders) == 1:
            self.neat_model.kill_trader(self.neat_model.traders[0], 'killing the last one')
            end_procedure('due to self.traders == 0')

        try:
            self.tick_position, self.tick_data = next(self.data_feeder.iterator)           
            self.neat_model.activate_traders(tick_data=self.tick_data)
            if self.display_graph:
                self.animation.step(tick_position = self.tick_position,
                                    tick_data = self.tick_data,
                                    n_traders = len(self.neat_model.traders),
                                    traders_bought = [len(i) for i in self.neat_model.traders_bought])

        except StopIteration: 
            end_procedure('due to end of iterator')

        

    def getData(self, stock , key, shortdataby=False):

        self.complete_data = stock_data(stock , key, shortdataby=shortdataby)
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
        self.indicators_to_use = {'RSI': [9],'MACD': ['12_24_9']}
        self.data_feeder = feeder(self.complete_data,self.indicators_to_use) #defines an iterator for the stock and indicators movements
        
    def report(self):
        
        self.sheet_name += 1
        
        traders_bought = self.neat_model.traders_bought
        traders_bought.insert(0,np.nan)
        
        if len(traders_bought) == len(self.data_feeder.data['close']):
            self.data_feeder.data['buys'] = traders_bought
            self.data_feeder.data.to_excel(self.writer, str(self.sheet_name))
            


if __name__ == '__main__':

    local_dir = os.path.dirname(__file__)
    NEAT_config_path = os.path.join(local_dir, 'mod_config-feedforward.txt')
    operation_config_path = os.path.join(local_dir, 'operations_config_file.txt')
    mymodel = run(NEAT_config_path , operation_config_path)
    
