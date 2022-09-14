# -*- coding: utf-8 -*-
"""
getstockdata.py:
- The primarly function of this module its the gathering and structure of the raw stock data from the web page.
"""
import pandas as pd
import numpy as np
import urllib.request
import json
import copy


class stock_data(object):
    
    def __init__(self, stock , key,  shortdataby=False):
        self.stock = stock
        self.key = key
        self.shortdataby = shortdataby
        
        self.original_data = self.call()
        self.data = copy.deepcopy(self.original_data)
        self.indicators = {}
        # self.data = self.randomizer()
        
        
    def call(self):
            
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol='+self.stock+'&outputsize=full&apikey=QXDW7T3QI0W3B9N5'
        # url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol='+self.stock+'&outputsize=compact&apikey=' + self.key
        
        data = json.loads(urllib.request.urlopen(url).read())
        original_df = pd.DataFrame.from_dict(data['Time Series (Daily)']).T
        
        original_df = original_df[['4. close','5. volume']]
        original_df = original_df.rename(columns={'4. close': 'close',
                                                  '5. volume': 'volume'})
                
        original_df = original_df.astype(float)
        original_df = original_df.iloc[::-1]
        if self.shortdataby: original_df = original_df.iloc[-int(self.shortdataby):]

        return original_df
    
    def calculate_SMA(self, window):
        
        df = self.data.rolling(window).mean()
        df = df.rename(columns={'close': 'sma_close_' + str(window),
                               'volume': 'sma_vol_' + str(window)})

        if not 'SMA' in self.indicators: self.indicators['SMA'] = {} #if this is the first SMA been created
            
        self.indicators['SMA'][window] = df
        
    def calculate_MACD(self,short_window, long_window, triger_line_days):
        
        df = copy.deepcopy(self.data)
        
        ewm_short = df['close'].ewm(span=short_window, adjust=False, min_periods=short_window).mean()
        ewm_long = df['close'].ewm(span=long_window, adjust=False, min_periods=long_window).mean()
        
        macd = ewm_short - ewm_long  #MACD line
        macd_s = macd.ewm(span=triger_line_days, adjust=False, min_periods=triger_line_days).mean() #MACD signal
        macd_d = macd - macd_s #Difference
        
        run_name = '%s_%s_%s' %(short_window,long_window,triger_line_days)
        
        df['macd_' + run_name] = df.index.map(macd)
        df['macd_s'+ run_name] = df.index.map(macd_s)
        df['macd_d'+ run_name] = df.index.map(macd_d)
        df = df[['macd_' + run_name,'macd_d'+ run_name,'macd_s'+ run_name]].round(4)
        
        if not 'MACD' in self.indicators: self.indicators['MACD'] = {} #if this is the first SMA been created
        
        
        self.indicators['MACD'][run_name] = df
        
    def calculate_RSI(self, periods, ema = True):
        """
        Returns a pd.Series with the relative strength index.
        """
        
        df = self.data
        
        close_delta = df['close'].diff()
    
        # Make two series: one for lower closes and one for higher closes
        up = close_delta.clip(lower=0)
        down = -1 * close_delta.clip(upper=0)
        
        if ema == True:
    	    # Use exponential moving average
            ma_up = up.ewm(com = periods - 1, adjust=True, min_periods = periods).mean()
            ma_down = down.ewm(com = periods - 1, adjust=True, min_periods = periods).mean()
        else:
            # Use simple moving average
            ma_up = up.rolling(window = periods, adjust=False).mean()
            ma_down = down.rolling(window = periods, adjust=False).mean()
            
        rsi = ma_up / ma_down
        rsi = round(100 - (100/(1 + rsi)),4)
        
        rsi = rsi.to_frame()
        rsi = rsi.rename(columns={'close':'rsi_close_' + str(periods)})
        
        if not 'RSI' in self.indicators: self.indicators['RSI'] = {} #if this is the first SMA been created       
        self.indicators['RSI'][periods] = rsi


class feeder(object):
    
    def __init__(self, stock_data_object, indicators_to_use, chunk_size=100):
        self.stock_data_object = stock_data_object
        self.indicators_to_use = indicators_to_use #dict {indicator_type: [indicaotor_name]} Ex: {'MACD':['12_42_9','24_186_12']}
        
        self.chunk_size = chunk_size
        
        self.data = self.merge_indicators()
        self.iterator, self.current_step = self.define_iterator()
        
    def merge_indicators(self):
        
        df_complete = copy.deepcopy(self.stock_data_object.data)
        
        for indicator_type in self.indicators_to_use:
            for indicator_name in self.indicators_to_use[indicator_type]:
                df_complete = df_complete.join(self.stock_data_object.indicators[indicator_type][indicator_name])
        
        return df_complete

        
    def define_iterator(self, initial_date=False):
                    
        self.botton_random_window = np.random.randint(1,len(self.stock_data_object.data)-self.chunk_size)
        self.upper_random_window = int(self.botton_random_window + self.chunk_size)
        self.data = self.data[self.botton_random_window : self.upper_random_window]
        iterator = self.data.iterrows()
        current_step = next(iterator)
        
        return iterator, current_step
        
    def next_step(self):
        self.current_step = next(self.iterator)