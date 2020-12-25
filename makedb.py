import pandas as pd
import numpy as np
from config import Config
import pickle
import sqlite3
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import re



class sab_kuch:
    def __init__(self):
        self.cfg = Config()     #Location wali class ka object
        #Database connection wagera banaya
        self.conn = self.make_db_conn(self.cfg.db_file)
        self.cur  = self.conn.cursor()
        self.mongo_client = self.make_mongo_conn()
        self.coll = self.mongo_client['med_articles'].articles_text
        self.conn.commit()
    
    # returns sqlite connection 
    def make_db_conn(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Exception as e:
            print(e)
        return conn

    def make_mongo_conn(self):
        return MongoClient()
    
    #Agle 4 function article ko clear karne ke liye hai taaki tf-idf bana sake
    def make_lower_case(self,text):
            return text.lower()

    def remove_stop_words(self, text):
        text = text.split()
        stops = set(stopwords.words("english"))
        text = [w for w in text if not w in stops]
        texts = [w for w in text if w.isalpha()]
        texts = " ".join(texts)
        return texts

    # Function for removing punctuation
    def remove_punctuation(self, text):
        tokenizer = RegexpTokenizer(r'\w+')
        text = tokenizer.tokenize(text)
        text = " ".join(text)
        return text

    # Function for removing the html tags
    def remove_html(self, text):
        html_pattern = re.compile('<.*?>')
        return html_pattern.sub(r'', text)


    # makes the tfidf matrix from the articles in the 
    # database
    #Scraped articles database me dalne ke baad uske cleaned text ke according tf-idf bana denge
    def make_tfidf_from_df(self, df):
        #Agar koi naya article publish hua hai to bhi ye function call hoga aur tf-idf ko update kardega
        vec = TfidfVectorizer(input='content', decode_error='replace',strip_accents='unicode', stop_words='english',ngram_range=(1,2), sublinear_tf=True)
        train_recs = list(df['cleaned_desc'].sample(frac=.5).values)
        vec.fit(train_recs)
        records = list(df['cleaned_desc'].values)
        X = vec.transform(records)
        pickle.dump(X,open('cfg.xfile','wb'))
        return


    #Saare scraped articles ko database me daalne ke liye
    def insert_records_to_db(self, df):
        for index,row in df.iterrows():
            self.cur.execute('insert into articles (title,keywords,text,ptime) values (?,?,?,?);',
                    (row['title'],row['keywords'],row['text'],row['ptime']))
            article_id = self.cur.lastrowid
            to_mongo = {'title':row['title'], 'keywords':row['keywords'],'text':row['text'], 'article_id':article_id}
            self.coll.insert_one(to_mongo)
        self.cur.execute('select count(*) from articles;')
        val = self.cur.fetchall()[0][0]
        self.cur.execute('insert into article_counts(num_articles) values (?);',(val,))
        self.make_tfidf_from_df(df)
        return 
        
    #Naye published article ko Database me insert karne ke liye
    def insert_record_to_dbx(self,df, title, keywords, text, ptime):
        self.cur.execute('insert into articles (title,keywords,text,ptime) values (?,?,?,?);',
                    (title,keywords,text,ptime))
        article_id = self.cur.lastrowid
        to_mongo = {'title':title, 'keywords':keywords,'text':text, 'article_id':article_id}
        self.coll.insert_one(to_mongo)
        self.cur.execute('select count(*) from articles;')
        val = self.cur.fetchall()[0][0]
        self.cur.execute('insert into article_counts(num_articles) values (?);',(val,))
        self.make_tfidf_from_df(df)
        return



    # returns pandas df with relevant columns from the raw medium 
    # csv file
    def build_articles_df(self, df):   
        #Scraped articles ko thoda bahut clean karke jo colums hame chahiye sirf wahi chun ne ke liye     
        df.drop(df.columns.difference(['title','keywords','text','cleaned_desc', 'ptime']),1,inplace=True)
        #data['cleaned_desc'] = data['text'].apply(func = make_lower_case)
        #data['cleaned_desc'] = data.cleaned_desc.apply(func = remove_stop_words)
        #data['cleaned_desc'] = data.cleaned_desc.apply(func=remove_punctuation)
        #data['cleaned_desc'] = data.cleaned_desc.apply(func=remove_html)
        #data = data.drop_duplicates(subset='cleaned_desc', keep='first', inplace=False)
        #df.drop_duplicates(subset = ['articleUrls'],inplace = True)
        df.drop_duplicates(subset = ['title'],inplace = True)
        df.dropna(inplace=True)
        df.reset_index(inplace = True)
        self.insert_records_to_db(df)
        return

    def check_to_do(self, check, articles_csv=None,title=None, keywords=None, text=None):
        #Jabhi bhi koi article publish hoga to ye function call karenge
        #Agar check me 1 aaya hai matlab scraped wale articles ko database me daal rahe hai
        # 0 ke case me koi naya article publish hua hai
        #Csv file scraped articles ki hai but jab koi naya article publish hoga to hum use csv aur
        #databse dono me add kardenge
        df = pd.read_csv(articles_csv)
        if(check==1):
            self.build_articles_df(df)
            #Saare scraped articles ko database me daalne ke liye
        else:
            #Naye article ke liye
            #pblish time bhi nikalke store karenge dataframe me taaki latest wale recommend kar sake
            now = datetime.now()
            ptime = now.strftime("%d/%m/%Y %H:%M:%S")
            cleaned = self.make_lower_case(text)
            cleaned = self.remove_stop_words(cleaned)
            cleaned = self.remove_punctuation(cleaned)
            cleaned = self.remove_html(cleaned)
            #Csv me insert kar dia pehle
            df1 = pd.DataFrame([title,keywords,text,cleaned, ptime])
            df = df.append(df1,ignore_index=True)
            #Database me insert karne ke liye
            self.insert_record_to_dbx(df,title,keywords,text,ptime)
        return