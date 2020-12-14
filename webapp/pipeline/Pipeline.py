import math
import numpy  as np
import pandas as pd
import joblib as jb

from scipy.sparse import hstack


class DataPipeline(object):
    
    def __init__(self):
        self.home_path = 'D:/01-DataScience/04-Projetos/00-Git/Youtube-Video-Recommendations/webapp/'
        self.titleVec  = jb.load(open(self.home_path + 'parameter/titleVec.pkl.z', 'rb'))
        self.modelLGBM = jb.load(open(self.home_path + 'model/modelLgbm.pkl.z', 'rb'))
        self.modelRf   = jb.load(open(self.home_path + 'model/modelRf.pkl.z', 'rb'))

    def dataCleaningRaw(self, df):
        df['LikeCount'] = df['LikeCount'].apply(lambda row: 0 if math.isnan(row) else row)
        df['UploadDate'] = pd.to_datetime(df['UploadDate'])
        df['DaysSincePublication'] = (pd.to_datetime('2021-01-01') - df['UploadDate']) / np.timedelta64(1,'D')
        return df



    def dataCleaning(self, dfFeatures):   
        dfFeatures['ViewCountIncidenceStack'].fillna(dfFeatures['ViewCountIncidenceStack'].mean(), inplace=True)
        dfFeatures['VotesStackLikeCount'].fillna(dfFeatures['VotesStackLikeCount'].mean(), inplace=True)
        return dfFeatures



    def featureSelection(self, df):
        df = DataPipeline.dataCleaningRaw(self, df)

        dfFeatures = pd.DataFrame(index=df.index)

        dfFeatures['ViewsPerDay'] = df['ViewCount'] / df['DaysSincePublication']

        dfFeatures['Duration'] = df['Duration']

        dfFeatures['ViewCountIncidenceStack'] = df['ViewCount'] / df['IncidenceStack']

        dfFeatures['VotesStackLikeCount'] = df['VotesStack'] * df['LikeCount']

        dfFeatures = DataPipeline.dataCleaning(self, dfFeatures)
        return dfFeatures

    def titleVectorizer(self, df, titleSeries):
        titleBowVec = self.titleVec.transform(titleSeries)
        dataWTitle = hstack([df, titleBowVec])
        return dataWTitle
    
    def getPrediction(self, modelLGBM, modelRf, orinalDataset, dataWTitle):
#         modelLGBM = self.modelLGBM
#         modelRf = self.modelRf
		modelLGBM = modelLGBM
        modelRf = modelRf
        pLgbm = modelLGBM.predict_proba(dataWTitle)[:,1]
        pRf = modelRf.predict_proba(dataWTitle)[:,1]
        pred = 0.5*pLgbm + 0.5*pRf
        dfResults = orinalDataset[['Title', 'WebpageUrl']].copy()
        dfResults['Predict'] = pred
        return dfResults