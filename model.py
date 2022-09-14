# -*- coding: utf-8 -*-
"""
Created on Wed Feb  2 17:30:48 2022

@author: JOSECG1
"""
import pandas as pd
import numpy as np
# from getstockdata import stock_data, feeder
# from Executor import ticker
# from animation import animated_graph
from portfolio import trader
import neat

class NEAT(object):
    
    def __init__(self, NEAT_config_file):
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                             neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             NEAT_config_file)
    
        # Create the population, which is the top-level object for a NEAT run.
        self.p = neat.Population(config)
    
        # Add a stdout reporter to show progress in the terminal.
        self.p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        self.p.add_reporter(stats)
        self.p.add_reporter(neat.Checkpointer(5))
        
        # self.winner = p.run(self.eval_genomes, 10)        
    
        
    def set_genomes(self, genomes, config):
        
        print('enter_eval_genomes')
        self.nets = []
        self.traders = []
        self.ge = []

        # initial_amount = 10000
        for genome_id, genome in genomes:
            # genome.fitness = initial_amount
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.nets.append(net)
            self.traders.append(trader(genome_id))
            self.ge.append(genome)
            
    def define_traders_parameters(self , traders_initial_amount , target_profit):
        
        self.traders_bought = []
        self.target_profit = target_profit
        for _,trader_ind in enumerate(self.traders):
            trader_ind.define_initial_amount(initial_amount = traders_initial_amount)
            # print('trader_ind position at the begging', trader_ind.trader_id)
            # print(trader_ind.position)
            
    def activate_traders(self , tick_data):
        '''
        self.traders_bought will be the lenght of the generator, and will have:
            list of traders buying in
            or nan
        '''
        
        self.traders_bought_sub = []
        for _,trader_ind in enumerate(self.traders):
            self.activate(trader_ind = trader_ind, tick_data = tick_data)
            
        if not self.traders_bought_sub:
            self.traders_bought_sub.append(np.nan)
            
        # self.traders_bought.append(len(self.traders_bought_sub))
        self.traders_bought.append(self.traders_bought_sub)
            
    def activate(self, trader_ind, tick_data):
        
        # def penalize_for_delay(self):
        #     trader_ind.
        
        output = self.nets[self.traders.index(trader_ind)].activate((tick_data['macd_12_24_9'],
                                                                     tick_data['macd_s12_24_9'],
                                                                     tick_data['macd_d12_24_9'], 
                                                                     tick_data['rsi_close_9']))

        if output[0] > 0.5:
            # print(output[0])
            succesfull_buy = trader_ind.buy( 1 , tick_data['close'])
            if succesfull_buy:
                print('trader buys ' , trader_ind.trader_id , tick_data['close'] , tick_data['close']*(1+self.target_profit))
                self.traders_bought_sub.append(trader_ind.trader_id)
            
        self.check_if_target_profit_reached(trader_ind , tick_data['close'])
        
        if trader_ind.available_amount<0 or \
            trader_ind.total_profit_losses<-200:
            reason = str(f"Kill trader {trader_ind.trader_id} as it does not passes check")
            self.kill_trader(trader_to_kill=trader_ind,
                             reason=reason)
            
    def check_if_target_profit_reached(self, trader_ind, price):
        
        # target_profit = target_profit
        df = trader_ind.position
        df['open_value'] = (price/df['price']) - 1
        time_to_sell = df['open_value'][df['open_value']>=self.target_profit].any()
        
        if time_to_sell:
            if trader_ind.current_status(price):
                print('trader sells ' , trader_ind.trader_id , df['price'][0] , price)
                # print(df)
        
            
    def report_positions(self):
        
        # columns_to_use = ['trader_id','quantity', 'average_price' ,'on_run_total_profit_losses','total_profit_losses']
        # columns_to_use = ['trader','quantity','price']
        # df_report = pd.DataFrame(columns=columns_to_use)
        
        for trader_ind in self.traders:
            trader_ind.get_total_profit_losses()
            fitness= trader_ind.total_profit_losses
            
            # if len(self.traders)>0 and fitness==0:
            #     fitness-=1000
            self.ge[self.traders.index(trader_ind)].fitness = fitness
            
            print('-------------------------')
            print('trader_ind.trader_id ' , trader_ind.trader_id)
            print('trader_ind.on_run_total_profit_losses ', trader_ind.on_run_total_profit_losses)
            print('trader_ind.total_profit_losses ',trader_ind.total_profit_losses)
            # print('trader_ind position at the end')
            # print(trader_ind.position)
            
            
            # data = [[trader_ind.trader_id , 
            #           # -trader_ind.total_quantity, 
            #           trader_ind.on_run_total_profit_losses,
            #           trader_ind.total_profit_losses]]
            
            # df_trader_id = pd.DataFrame(data=data)
            
            # df_trader_id = pd.DataFrame(data=trader_ind.position)
            # df_trader_id['trader'] = trader_ind.trader_id
            
            # # df_report = df_report.append(df_trader_id,ignore_index=True)
            # frames = [df_report, df_trader_id]
            # df_report = pd.concat(frames)
            
        # print(df_report)
            
    def kill_trader(self, trader_to_kill, reason):
        '''
        trader_to_kill needs a trader obj
        '''
        print(reason)
        self.nets.pop(self.traders.index(trader_to_kill))
        self.ge.pop(self.traders.index(trader_to_kill))
        self.traders.pop(self.traders.index(trader_to_kill))      
            
    def kill_lowest_fitness(self):
        
        if len(self.traders)>1: #if there its at least 1 trader
            print("len(self.traders) - " , len(self.traders))
            for num in range(0,int(len(self.traders)/2)):
                lowest_fitness = 9999999999999999999
                
                for i,trader_ind in enumerate(self.traders):
                    fitness_level = self.ge[self.traders.index(trader_ind)].fitness
                    
                    if fitness_level < lowest_fitness:
                        lowest_fitness = fitness_level
                        trader_with_lowest_fitness = trader_ind
                
                trader_id_with_lowest_fitness = round(trader_with_lowest_fitness.trader_id)
                reason = str(f"Kill trader {trader_id_with_lowest_fitness} as it has the lowest fitness {lowest_fitness}")
                self.kill_trader(trader_to_kill=trader_with_lowest_fitness,
                                 reason = reason)
