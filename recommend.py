from sklearn.neighbors import NearestNeighbors
import pickle
import pandas as pd
import numpy as np


class Rec:

    def __init__(self,db,xfile,num_recs):
        self.db = db
        self.X = pickle.load(open(xfile,'rb'))
        self.num_recs = num_recs

    def _get_user_yvec(self,user_id):
        # gets the user's saved articles and encodes to a one-hot target vector
        rows = self.db.get_user_articles(user_id)
        if len(rows) == 0: return None
        articles = np.array([rows[i]['article_id'] for i in range(len(rows))])
        num_articles = self.db.get_article_counts()
        y = np.zeros(num_articles)
        y[articles] = 1
        return y
        #return articles

    def get_user_recs(self,user_id):
        abc="recommendations"
        return abc



    def get_article_recs(self,article_id, user_id):
        self.idx=article_id
        model_tf_idf = NearestNeighbors(algorithm='brute', metric='cosine')
        model_tf_idf.fit(self.X)
        distances, indices = model_tf_idf.kneighbors(self.X[self.idx], n_neighbors=100)
        neighbors = pd.DataFrame({'distance':distances.flatten(), 'id':indices.flatten()})
        yvec = self._get_user_yvec(user_id)
        neighbors.sort_values("distance", axis = 0, ascending = True, inplace = True) 
        rec_ind = neighbors['id'].to_numpy()
        rec_ind = list(rec_ind.flatten()) 
        xyz=np.where(yvec==1)
        xyz = np.asarray(xyz)
        xyz = xyz.flatten()
        xyz = xyz.tolist()
        matches = list(set(rec_ind) & set(xyz))
        final_rec=list(set(rec_ind)-set(matches))
        #rec_ind[np.where(yvec == 1)] = float('-inf')
        #final_rec = [i for i in rec_ind if(i is not float('-inf'))]
        return final_rec
