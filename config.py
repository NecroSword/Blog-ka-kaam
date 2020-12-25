class Config:
    
    def __init__(self):
        self.xfile = './data/X.pkl'             #TF-IDF ke pickle file ki location
        self.db_file = 'med_db.db'                #Database ki location
        self.data_path = './data/articles.csv'         #Scraped data ki location
        self.num_articles_home = 100            #Home pe itne articles chahite
        self.num_recs = 100                     #Itni recommendations
