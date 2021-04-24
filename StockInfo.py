#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 16:51:43 2021

@author: jaeyeonpyo
"""

import numpy as np
import pandas as pd
import nltk
#nltk.download('stopwords')
from nltk.corpus import stopwords
import re
import yahoo_fin.stock_info as yf

from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import word_tokenize, sent_tokenize
import bs4
from bs4 import BeautifulSoup
import time
import datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA


# ticker includes NYSE and NASDAQ ticker symbols 
# https://www.nasdaq.com/market-activity/stocks/screener?exchange=nasdaq&letter=0&render=download
ticker = pd.DataFrame(pd.read_csv("nasdaq_screener_1618514462322.csv", usecols=["Symbol"]))
ticker = ticker.append(pd.read_csv("nasdaq_screener_1618514479024.csv", usecols=["Symbol"]))
ticker.index = list(ticker["Symbol"])

tickerlist = ticker.values
tickerset = set(tickerlist.flatten())

#Source: https://www.kaggle.com/gpreda/reddit-wallstreetsbets-posts
text_data = pd.DataFrame(pd.read_csv('reddit_wsb.csv'))
text_data['Date'] = [x[0:10] for x in text_data['timestamp']]

#Robinhood 50 stocks that were limited in trading 
#Source: 
#https://finance.yahoo.com/news/robinhood-expands-trading-restrictions-50-225241993.html

rh50 = [
"AAL", 
"ACB", 
"AG", 
"AMC", 
"AMD", 
"BB", 
"BBBY", 
"BYDDY", 
"BYD", 
"BYND", 
"CCIV", 
"CLOV", 
"CRIS", 
"CTRM", 
"EXPR", 
"EZGO", 
"GME", 
"GTE", 
"GME", 
"HIMS", 
"INO", 
"IPOE", 
"IPOF", 
"JAGX", 
"KOSS", 
"LLIT", 
"MRNA", 
"NAKD", 
"NCTY", 
"NOK", 
"NVAX", 
"OPEN", 
"RKT", 
"RLX", 
"RYCEY", 
"SBUX", 
"SHLS", 
"SIEB", 
"SLV", 
"SNDL", 
"SOXL", 
"SRNE", 
"STPK", 
"TGC", 
"TRIX", 
"TR", 
"TRVG", 
"WKHS", 
"XM", 
"ZOM"]


stop_words = stopwords.words('english')

# additional stop words that mean something else 
additional_stop_words = ['ceo', 'abc', 'low', 'very', 're', 'turn', 'snow', 'iii', 'em', 
                   'ach', 'by', 'gogo', 'or', 'out', 'gold', 'infp', 'all', 'tell', 'salfe', 'team', 'he', 'at', 'post', 
                   'st', 'fe', 'fl', 'go', 'dis', 'new', 'ta', 'good', 'dis', 'see', 'cash', 'pm', 'free', 
                   'huge', 'ride', 'tv', 'love', 'dm', 'ever', 'eod', 'iq', 'usa', 'link', 'et', 'xl', 'live', 
                   'riot', 'fcf', 'root', 'dd', 'one', 'ai', 'sa', 'real', 'ip', 'next', 'si', 'uk', 'stay', 'mo', 
                   'big', 'open', 'plug', 'edit', 'jp', 'rh', 'pt']

for i in range(len(additional_stop_words)): 
    stop_words.append(additional_stop_words[i])
    
    
# accumulate all text from reddit into a list and get a list of tickers discussed more than 50 times 
# during the period specified, then see which of those are rh50 stocks 
text = []
discussed_ticker = []

for i in range(len(text_data)):
    text.append(text_data['body'][i])

text = [x for x in text if pd.notnull(x)]

result = {}
                    
# =============================================================================
# def getTickerFreq(comment_list):
#     tokenizer = RegexpTokenizer(r'\w+')
#     for s in comment_list:
#         flag = False
#         if flag == False: 
#             for w in tokenizer.tokenize(s):
#                 if w in tickerset and len(w) > 1:
#                     if not w in result.keys():
#                         result[w] = 1
#                         break
#                     else:
#                         result[w] += 1
#                         break
#     return result
# =============================================================================

def getTickerFreq(comment_list):
    tokenizer = RegexpTokenizer(r'\w+')
    for c in comment_list:     
        s = tokenizer.tokenize(c)
        for ticker in final_ticker: 
            if ticker in s:
                if not ticker in ticker_msg.keys():
                    ticker_msg[ticker] = 1
                else:
                    ticker_msg[ticker] += 1
    return result
    

getTickerFreq(text)
result_filtered = {x for x in result if result.get(x) > 10}

result_filtered_stopwords_removed = []
for word in result_filtered: 
    if word.lower() not in stop_words:
        result_filtered_stopwords_removed.append(word)

final_ticker = result_filtered_stopwords_removed
final_ticker_rh50 = [x for x in final_ticker if x in rh50]

pd.DataFrame(final_ticker).to_csv('final_ticker.csv')
pd.DataFrame(final_ticker_rh50).to_csv('final_ticker_rh50.csv')

#historical stock prices by date for each ticker

# Data from January 1, 2021 chosen since it was when the stocks showed unusual activity based on Reddit's "rebel"
period1 = int(time.mktime((datetime.date(2021, 1, 28)).timetuple()))
period2 = int(time.mktime((datetime.date(2021, 4, 5)).timetuple()))

data = pd.DataFrame()
for i in range(len(final_ticker)): 
    tkr = final_ticker[i]
    query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{tkr}?period1={period1}&period2={period2}&interval=1d&events=history&includeAdjustedClose=true'
    df = pd.read_csv(query_string)
    df['ticker'] = tkr
    data = data.append(df)

data['rh50'] = 0

data = data.reset_index()
data = data[['ticker', 'Date', 'Open', 'Close', 'High', 'Low']]
data['price_change'] = data['Close'] / data['Open']


text_data = text_data.dropna()
text_data = text_data.reset_index()
text_data = text_data[['Date', 'body']]

text_data.to_csv('reddit_text.csv')
data.to_csv('daily_stock_price.csv')

# accounting terms 
acctg = ['earnings', 'cash', 'revenue', 'dividend','div', 'buyback', 'p/e', 'pe', 'current report', 'asset', 'eps', 'periodic report', 'cash flow', 'fcf', 'cf', 'inventory', 'expense', 'impair', 'balance sheet', 'analyst', 'accounting', 'leverage', 'control', 'profit', 'book value', 'stock option', 'income', 'guidance', 'fair value', 'liability', 'lease', 'R&D', 'capex', 'audit', 'ebit', 'depreciate', 'gaap', 'financial instrument', 'unusual']

# Get how many times each ticker was discussed, and of those, how many involved accounting terms in message
#ticker_msg = {}
#ticker_acctg_msg = {}
                    
# =============================================================================
# def getDiscussedFreq(comment_list):
#     tokenizer = RegexpTokenizer(r'\w+')
#     for s in comment_list:
#         for w in tokenizer.tokenize(s):
#             if w in final_ticker and len(w) > 1:
#                 if not w in ticker_msg.keys():
#                     ticker_msg[w] = 1
#                 else:
#                     ticker_msg[w] += 1
#                 for a in acctg : 
#                     if a in tokenizer.tokenize(s):
#                         if not w in ticker_acctg_msg.keys():
#                             ticker_acctg_msg[w] = 1
#                             break
#                         else: 
#                             ticker_acctg_msg[w] += 1
#                             break
#                         break
#     return ticker_msg, ticker_acctg_msg
# =============================================================================


# =============================================================================
# def getDiscussedFreq(comment_list):
#     tokenizer = RegexpTokenizer(r'\w+')
#     for c in comment_list:     
#         s = tokenizer.tokenize(c)
#         for ticker in final_ticker: 
#             if ticker in s:
#                 flag = False
#                 if not ticker in ticker_msg.keys():
#                     ticker_msg[ticker] = 1
#                 else:
#                     ticker_msg[ticker] += 1
#                 for a in acctg: 
#                     if flag == False:
#                         if a in s : 
#                             if not ticker in ticker_acctg_msg.keys():
#                                 ticker_acctg_msg[ticker] = 1
#                                 flag = True
#                                 break
#                             else:
#                                 ticker_acctg_msg[ticker] += 1
#                                 flag = True          
#     return ticker_msg, ticker_acctg_msg
# =============================================================================


def getDiscussedFreq(comment_list):
    tokenizer = RegexpTokenizer(r'\w+')
    for c in comment_list:     
        s = tokenizer.tokenize(c)
        for ticker in final_ticker: 
            if ticker in s:
                flag2 = False
                if not ticker in ticker_msg.keys():
                    ticker_msg[ticker] = 1
                else:
                    ticker_msg[ticker] += 1
                for a in acctg: 
                    if flag2 == False:
                        if a in s : 
                            if not ticker in ticker_acctg_msg.keys():
                                ticker_acctg_msg[ticker] = 1
                                flag2 = True
                                break
                            else:
                                ticker_acctg_msg[ticker] += 1
                                flag2 = True
                                break
    return ticker_msg, ticker_acctg_msg


ticker_msg, ticker_acctg_msg = getDiscussedFreq(text)

df_ticker_msg = pd.DataFrame(ticker_msg.items(), columns = ['ticker', 'total_msg'])
df_ticker_acctg_msg = pd.DataFrame(ticker_acctg_msg.items(), columns = ['delete', 'acctg_msg'])
ticker_text_analysis = pd.concat([df_ticker_msg, df_ticker_acctg_msg], axis=1)
ticker_text_analysis = ticker_text_analysis.drop(columns = 'delete')


ticker_text_analysis["rh50"] = np.where(ticker_text_analysis["ticker"].isin(final_ticker_rh50), 1, 0)


#Get accounting information for each ticker
#remove some tickers that had YahooFinance issues, then add accounting info manually at the end 
#tmp_remove = ['NIO', 'BLNK', 'TTM', 'TDA', 'PLTR', 'PT']
tmp_remove = ['PLTR']
for i in range(len(tmp_remove)): 
    final_ticker.remove(tmp_remove[i])

acctginfo = []

def getAcctgInfo(ticker):
    global balance_sheet
    global income_statement
    global cfs
    global periods
    balance_sheet = yf.get_balance_sheet(ticker, yearly = False)
    income_statement = yf.get_income_statement(ticker, yearly = False)
    cfs = yf.get_cash_flow(ticker, yearly = False)
    periods = balance_sheet.columns
    cq = periods[0]
    pq = periods[1]
    cq_rev = income_statement[periods[0]]['totalRevenue']
    pq_rev = income_statement[periods[1]]['totalRevenue']
    cq_ni = income_statement[periods[0]]['netIncome']
    pq_ni = income_statement[periods[1]]['netIncome']
    cq_cash = balance_sheet[periods[0]]['cash']
    pq_cash = balance_sheet[periods[1]]['cash']
    cq_ocf = cfs[periods[0]]['totalCashFromOperatingActivities']
    pq_ocf = cfs[periods[1]]['totalCashFromOperatingActivities']
    acctginfo.append((ticker, cq, pq, cq_rev, pq_rev, cq_ni, pq_ni, cq_cash, pq_cash, cq_ocf, pq_ocf))

#had issues with the below data extract from yahoo finance
#earnings_date, cq_rev, eps_actual, eps_estimate, eps_surprise, 
#pq_fcf, cq_fcf


for ticker in final_ticker:
    print(ticker)
    getAcctgInfo(ticker)    


acctg_ticker = pd.DataFrame(acctginfo, columns = ['ticker', "cq", "pq", "cq_rev", "pq_rev", "cq_ni", "pq_ni", "cq_cash", "pq_cash", "cq_ocf", "pq_ocf"])
#"earnings_date", "eps_actual", "eps_estimate", "eps_surprise",

text_acctg_combined = pd.merge(ticker_text_analysis, acctg_ticker, on = 'ticker', how = 'outer')

text_acctg_combined.to_csv("text_acctg_combined.csv")

