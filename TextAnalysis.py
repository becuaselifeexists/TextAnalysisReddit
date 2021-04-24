#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: jaeyeonpyo
"""

import numpy as np
import pandas as pd
import yahoo_fin.stock_info as yf
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import text2emotion as te


text_data = pd.read_csv('reddit_text.csv')
text_data = text_data[['Date', 'body']]
data = pd.read_csv('daily_stock_price.csv')
final_ticker = pd.read_csv('final_ticker.csv')['0'].to_list()
final_ticker_rh50 = pd.read_csv('final_ticker_rh50.csv')['0'].to_list()

tokenizer = RegexpTokenizer(r'\w+')

text_by_ticker_date = data[['ticker', 'Date']]
    
text = []

for i in range(len(text_data)):
    text.append(text_data['body'][i])

text_only = [x for x in text if pd.notnull(x)]

sid = SIA()

sentiment_analysis = []

for index, row in text_data.iterrows():
    for ticker in final_ticker: 
        text = row['body']
        token = tokenizer.tokenize(text)
        if ticker in token :
            date = row['Date']
            print(date)
            happy = te.get_emotion(text).get('Happy')
            angry = te.get_emotion(text).get('Angry')
            surprise = te.get_emotion(text).get('Surprise')
            sad = te.get_emotion(text).get('Sad')
            fear = te.get_emotion(text).get('Fear')
            pos = sid.polarity_scores(text).get('pos')
            neg = sid.polarity_scores(text).get('neg')
            neu = sid.polarity_scores(text).get('neu')
            compound = sid.polarity_scores(text).get('compound')
# =============================================================================
#             positive = 0
#             negative = 0
#             for w in token: 
#                 w = w.upper()
#                 if w in negative_words: 
#                     negative += 1
#                 if w in positive_words: 
#                     positive += 1
# =============================================================================
            sentiment_analysis.append((ticker, date, pos, neg, neu, compound, happy, angry, surprise, sad, fear))
#positive, negative, 

text_sentiment_analysis_df = pd.DataFrame(sentiment_analysis, columns = ['ticker', 'date', 'positive', 'negative', 'neutral', 'compound', 'happy', 'angry', 'surprise', 'sad', 'fear'])
text_sentiment_analysis_df["rh50"] = np.where(text_sentiment_analysis_df["ticker"].isin(final_ticker_rh50), 1, 0)
text_sentiment_analysis_df.to_csv("text_sentiment_analysis.csv")

