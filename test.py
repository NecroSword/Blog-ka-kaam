
#Experiment ke liye

import numpy as np

a=np.array([3, 5, 6, 7])
b=np.zeros(20)

b[a] = 1
print(b)
c = np.array([7,1,8,3,7,44,22,1,6,89,9], dtype=float)
c[np.where(b==1)]=float('-inf')
print(c)

'''
from datetime import datetime
from gensim.summarization import keywords
import pandas as pd


class TextRankImpl:

    def init(self, text):
        self.text = text

    def getKeywords(self):
        return (keywords(self.text).split('\n'))

data = pd.read_csv('./data/articles.csv')
textRankImpl = TextRankImpl(data['cleaned_desc'].iloc[0])
print (textRankImpl.getKeywords())
print (textRankImpl.getKeywords()[:10])
# datetime object containing current date and time
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
print("date and time =", dt_string)
'''