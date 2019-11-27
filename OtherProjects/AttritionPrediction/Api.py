# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 15:18:54 2019

@author: Venkata.Gedda
"""

from flask import Flask, request
import pandas as pd
#import json
#from Final import Final_Fun
from api_code_attrpr import attrition_prediction
app = Flask(__name__)

@app.route("/hello")
def hello():
    return "Attrition!!"

@app.route('/Attrition', methods=['POST'])
def attritionPrediction():
    json_input = request.get_json(force = True)
    json_df = pd.DataFrame(json_input, index = [0])
    final_df = attrition_prediction(json_df)
    json_out=final_df.to_json(orient='records')
    return json_out

if __name__ == '__main__':
    app.run(port=5019,debug=False)

