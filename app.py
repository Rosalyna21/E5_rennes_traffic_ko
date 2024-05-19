from flask import Flask, render_template, request
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import logging
from logging.handlers import RotatingFileHandler
import flask_monitoringdashboard as dashboard


# from keras.models import load_model
from tensorflow.keras.models import load_model
"""Modification de l'import"""

from src.get_data import GetData
from src.utils import create_figure, prediction_from_model 



app = Flask(__name__)

dashboard.config.init_from(file='config.cfg')


data_retriever = GetData(url="https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/exports/json?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B")
data = data_retriever()

model = load_model('model.h5') 


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':

        fig_map = create_figure(data)
        graph_json = fig_map.to_json()

        selected_hour = request.form['hour']
        selected_hour = int(selected_hour)
        
        cat_predict = prediction_from_model(model,selected_hour)

        color_pred_map = {0:["Prédiction : Libre", "green"], 1:["Prédiction : Dense", "orange"], 2:["Prédiction : Bloqué", "red"]}

        return render_template('home.html', graph_json=graph_json, text_pred=color_pred_map[cat_predict][0], color_pred=color_pred_map[cat_predict][1])

    else:

        fig_map = create_figure(data)
        graph_json = fig_map.to_json()

        return render_template('home.html', graph_json=graph_json)

# import psutil

# @dashboard.app.route('/dashboard/custom_alerts')
# def custom_alerts():
#     # Check CPU and Memory usage
#     cpu_usage = psutil.cpu_percent(interval=1)
#     memory_info = psutil.virtual_memory()
#     memory_usage = memory_info.percent

#     alerts = []
#     if cpu_usage > 80:
#         alerts.append(f"High CPU usage detected: {cpu_usage}%")
#     if memory_usage > 75:
#         alerts.append(f"High Memory usage detected: {memory_usage}%")

#     return dashboard.blueprints.utils.make_json_response(alerts)

# # Register the custom alert function
# dashboard.config.add_custom_alert('custom_alerts', '/dashboard/custom_alerts')

# import logging
# from logging.handlers import RotatingFileHandler

# handler = RotatingFileHandler('flask_monitoring.log', maxBytes=10000, backupCount=1)
# handler.setLevel(logging.WARNING)
# app.logger.addHandler(handler)

# @dashboard.app.route('/dashboard/check_thresholds')
# def check_thresholds():
#     response_time = dashboard.data.get_response_time()
#     error_rate = dashboard.data.get_error_rate()
#     requests_per_second = dashboard.data.get_requests_per_second()

#     if response_time > 500:
#         app.logger.warning(f"High response time detected: {response_time}ms")
#     if error_rate > 1:
#         app.logger.warning(f"High error rate detected: {error_rate}%")
#     if requests_per_second > 10:
#         app.logger.warning(f"High requests per second detected: {requests_per_second}rps")

#     return "Thresholds checked."

# # Register the check thresholds function
# dashboard.config.add_custom_alert('check_thresholds', '/dashboard/check_thresholds')

dashboard.bind(app)

if __name__ == '__main__':

    app.run(debug=True)

