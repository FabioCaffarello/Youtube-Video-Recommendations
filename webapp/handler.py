import os
import joblib as jb
import pandas as pd

from flask import Flask, request, Response

from pipeline.Pipeline import DataPipeline



modelLGBM = jb.load(open('model/modelLgbm.pkl.z', 'rb'))
modelRf   = jb.load(open('model/modelRf.pkl.z', 'rb'))


# Initialize API
app = Flask(__name__)

@app.route('/video/predict', methods=['POST'])
def youtubePredict():
	testJSON = request.get_json()
	
	if testJSON: #there is data
        if isinstance(testJSON, dict):
            df = pd.DataFrame(testJSON, index=[0]) #unique example
        else:
            df = pd.DataFrame(testJSON, columns=testJSON[0].keys()) #multiple examples
    
        # Instantiate
        pipeline = DataPipeline()
        
        # Data Cleaning & Feature Engineering
        df1 = pipeline.featureSelection(df)
        #  Title Vectorizer
        df2 = pipeline.titleVectorizer(df1, df['Title'])
        # Prediction
        dfResponse = pipeline.getPrediction(modelLGBM, modelRf, df, df2)

        return dfResponse
    
    else:
        return Response('{}', status=200, mimetype='application/json')
	
	
if __name__ == '__main__':
    port = os.environ.get( 'PORT', 5000)
    app.run(host='0.0.0.0', port=port)