from flask import Flask, render_template, request
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_monitoringdashboard import Dashboard

# from keras.models import load_model
from tensorflow.keras.models import load_model
"""Modification de l'import"""

from src.get_data import GetData
from src.utils import create_figure, prediction_from_model 

app = Flask(__name__)
Dashboard(app)

# Configuration du logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
app.logger.addHandler(handler)

data_retriever = GetData(url="https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/exports/json?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B")
data = data_retriever()

model = load_model('model.h5') 

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':

        fig_map = create_figure(data)
        graph_json = fig_map.to_json()

        selected_hour = request.form['hour']
        # Vérifiez le type de selected_hour
        # print(type(selected_hour))
        selected_hour = int(selected_hour)
        
        cat_predict = prediction_from_model(model,selected_hour)

        color_pred_map = {0:["Prédiction : Libre", "green"], 1:["Prédiction : Dense", "orange"], 2:["Prédiction : Bloqué", "red"]}

        return render_template('home.html', graph_json=graph_json, text_pred=color_pred_map[cat_predict][0], color_pred=color_pred_map[cat_predict][1])

    # cat_predict = prediction_from_model(model)->cat_predict = prediction_from_model(model,selected_hour)
    else:

        fig_map = create_figure(data)
        graph_json = fig_map.to_json()#<-

        return render_template('home.html', graph_json=graph_json)

if __name__ == '__main__':
    app.run(debug=True)

