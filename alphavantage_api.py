

import requests
import json
import numpy as np
import pandas as pd

class ts_stock(): #time series data related to the stock
    def __init__(self,date,high,low,close,volume): #vanilla initiation of variables
        self._date_ = date
        self._high_ = high
        self._low_ = low
        self._close_ = close
        self._volume_ = volume
   #setters/getters
    def set_date(self,new_date):
        self._date_ = new_date
    def get_date(self):
        return self._date_
    def set_high(self,new_high):
        self._high_ = new_high
    def get_high(self):
        return self._high_
    def set_low(self,new_low):
        self._low_ = new_low
    def get_low(self):
        return self._low_
    def set_close(self,new_close):
        self._close_ = new_close
    def get_close(self):
        return self._close_
    def set_volume(self,new_volume):
        self._volume_ = new_volume
    def get_volume(self):
        return self._volume_
    def __repr__(self):
        return "Date:{date}, High:{high}, Low:{low}, Close:{close}, Volume:{volume}".format(date = self.get_date(), high = self.get_high(), low = self.get_low(), close = self.get_close(), volume = self.get_volume())
    def __str__(self):
        return "Date:{date}, High:{high}, Low:{low}, Close:{close}, Volume:{volume}".format(date = self.get_date(), high = self.get_high(), low = self.get_low(), close = self.get_close(), volume = self.get_volume())

'''
Request json through requests package from alphavantage website (https://www.alphavantage.co/)
'''
def request_json(stock,period):
    key =  #request api key here: https://www.alphavantage.co/support/#api-key
    url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval={period}min&apikey={key}&datatype=json".format(ticker = stock, period = period, key = key)    
    data = requests.get(url)
    response = json.loads(data.content.decode('utf-8'))
    return response
    
'''
parse json for relevant data, can be expanded through more comprehension
'''
def parse_json(json):
    interval = json["Meta Data"]["4. Interval"]
    ticker = json["Meta Data"]["2. Symbol"]
    ts_data = json["Time Series ({})".format(interval)]
    lst = list()
    for date in ts_data: #parses every entry in the time-series dataset
        high = ts_data[date]["2. high"]
        low = ts_data[date]["3. low"]
        close = ts_data[date]["4. close"]
        volume = ts_data[date]["5. volume"]
        pit = ts_stock(date,high,low,close,volume) #create point-in-time object
        lst.append(pit) 
    return (ticker,lst) #tuple of ticker and data list for further processing

'''
Standard Deviation of the security, moreso a practice in NumPy methods
'''
def std_dev(stock_dict):
    print("The stocks currently stored are\n")
    for key in stock_dict: #shows stocks already processed
        print(key)
    ticker = input("What ticker would you like to compute the standard deviation of?\n")
    company_data = stock_dict[ticker.upper()]
    close_list = list() #creates a list of close prices
    for ts_data in company_data: 
        close_list.append(float(ts_data.get_close())) #appends close at each date
    close_list_pct = pd.DataFrame(close_list).pct_change()
    close_np = np.array(close_list_pct[1:])
    return close_np.std()

'''
Adds security to processed dictionary for a given periodicity
'''
def add_stock(dictionary):

    stock = input("What stock would you like to search for?\n")
    period = input("What periodic time series do you want to view?\n(1, 5, 15, 30, 60 mins)\n")
    to_parse = request_json(stock,period) #request data from website
    info_tup = parse_json(to_parse) #process
    ticker = info_tup[0].upper() #always defaults to uppercase ticker
    lst = info_tup[1] 
    dictionary[ticker] = lst #k,v pair as ticker and processed data
    return (stock,period)

'''
Attempts to calculate how security moves relative to SPY as a proxy for the market
'''
def calc_beta(stock_dict):
    market_dat = stock_dict["SPY"] #market proxy data
    comp_tick = input("What company would you like to compute the Beta of?\n")
    comp_dat = stock_dict[comp_tick.upper()] #comparison data
    mkt_close_list = list()
    comp_close_list = list()
    for ts_data in market_dat: #get close for each market period
        mkt_close_list.append(float(ts_data.get_close()))
    mkt_close_pct = pd.DataFrame(mkt_close_list).pct_change() #convert to percent change
    for ts_data in comp_dat: #get close for each comparison period
        comp_close_list.append(float(ts_data.get_close()))
    comp_close_pct = pd.DataFrame(comp_close_list).pct_change() #convert to percent change
    
    mkt_series = pd.Series(mkt_close_pct[0][1:]) #convert DF to series for calc
    comp_series = pd.Series(comp_close_pct[0][1:]) # convert DF to series for calc
    covar = mkt_series.cov(comp_series) #covariance of market to comparison
    var_mkt = mkt_series.var() #variance of market
    beta = covar / var_mkt #Beta equation
    print("The Beta of {} is {}".format(comp_tick,beta)) #fprint
    return beta

'''
Exports relevant relevant information to csv file
'''  
def export_file(stock_dict):
    ticker = input("What company would you like to export the data of?\n")
    tick_up = ticker.upper()
    tick_dat = stock_dict[tick_up] #company data as ts objects
    date_list = list() #initialize lists for insertion into dataframe
    high_list = list()
    low_list = list()
    close_list = list()
    volume_list = list()
    for ts_data in tick_dat: #loop through each date for info, append to lists
        date_list.append(ts_data.get_date())
        high_list.append(float(ts_data.get_high()))
        low_list.append(float(ts_data.get_low()))
        close_list.append(float(ts_data.get_close()))
        volume_list.append(float(ts_data.get_close()))
        
    exp_df = {"Date": date_list, #create export DF framework
              "High": high_list,
              "Low": low_list,
              "Close":close_list,
              "Volume": volume_list}
    to_exp = pd.DataFrame(exp_df, columns = ["Date","High","Low","Close","Volume"]) #convert to DF
    to_exp.to_csv("test.csv", index = False) #export as csv file to working directory

'''
Menu function for easier call structure
'''
def menu(): 
    prompt = "What would you like to do?\n1: Add Stock\n2:Compute Standard Deviation\n3:Compute Beta\n4:Export to CSV\n5:Quit\n"
    choice = input(prompt)
    return int(choice) #uses ints, could enum class

def main():
    stock_dict = dict()
    to_parse = request_json("SPY","60") #initialize dict with market proxy
    info_tup = parse_json(to_parse)
    lst = info_tup[1]
    stock_dict["SPY"] = lst
    print("Alphavantage Interface 1.0")
    
    choice = menu() #first menu call, will exit loop on input criteria
    while choice != 5:
        if choice == 1:                
            add_stock(stock_dict)
            choice = menu()
        elif choice == 2: 
            stdev = std_dev(stock_dict)
            print(stdev)
            choice = menu()
        elif choice == 3:
            beta = calc_beta(stock_dict)
            choice = menu()
        elif choice == 4:
            export_file(stock_dict)
            choice = menu    
main()
