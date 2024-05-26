from flask import Flask, render_template, request
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import logging
from logging.handlers import RotatingFileHandler
import flask_monitoringdashboard as dashboard
import os
import pandas as pd
from tensorflow.keras.models import load_model
from apscheduler.schedulers.background import BackgroundScheduler

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.get_data import GetData
from src.utils import create_figure, prediction_from_model

app = Flask(__name__)

dashboard.config.init_from(file='config.cfg')

data_url = "https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/exports/json?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B&apikey=51fc720694959be3dee39ba8e515826ab669377a28f3f79227970508"

model_path = 'model.h5'

# Configuration du logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

# Récupération et traitement des données
def fetch_data(url):
    try:
        app.logger.info("Fetching data...")
        data_retriever = GetData(url=url)
        data = data_retriever()
        if data.empty:
            app.logger.error("Fetched data is empty")
        return data
    except Exception as e:
        app.logger.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Chargement du modèle
def load_prediction_model(path):
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        model = load_model(path)
        return model
    except Exception as e:
        app.logger.error(f"Error loading model: {e}")
        return None

# Initialiser les données et le modèle
data = fetch_data(data_url)
model = load_prediction_model(model_path)

# Tâche planifiée pour exécuter la fonction fetch_data toutes les 30 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_data, 'interval', minutes=30, args=[data_url])
scheduler.start()

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if data.empty:
            raise ValueError("Data is empty")
        if model is None:
            raise ValueError("Model not loaded")

        fig_map = create_figure(data)
        graph_json = fig_map.to_json()

        if request.method == 'POST':
            selected_hour = int(request.form['hour'])
            cat_predict = prediction_from_model(model, selected_hour)
            color_pred_map = {0: ["Prédiction : Libre", "green"], 1: ["Prédiction : Dense", "orange"], 2: ["Prédiction : Bloqué", "red"]}
            text_pred, color_pred = color_pred_map[cat_predict]
        else:
            text_pred, color_pred = None, None

        return render_template('home.html', graph_json=graph_json, text_pred=text_pred, color_pred=color_pred)
    except Exception as e:
        app.logger.error(f"Error in index route: {e}")
        return render_template('error.html', error=str(e))
    
@app.route('/send-email')
def send_email():
    name = "Jean"
    HOST = "smtp-mail.outlook.com"
    PORT = 587

    FROM_EMAIL = "rennesapplication@outlook.fr"
    TO_EMAIL = 'aude.bouchonnet@laposte.net'
    PASSWORD = "AzErTy159753!"

    message = MIMEMultipart("alternative")
    message['Subject'] = "testing"
    message['From'] = FROM_EMAIL
    message['To'] = TO_EMAIL


    html = ""
    with open("mail.html", "r") as file:
        html = file.read()

    html_part = MIMEText(html, 'html')
    message.attach(html_part)

    smtp = smtplib.SMTP(HOST, PORT)

    status_code, response = smtp.ehlo()
    print(f"[*] Echoing the server: {status_code} {response}")

    status_code, response = smtp.starttls()
    print(f"[*] Starting TLS connection: {status_code} {response}")

    status_code, response = smtp.login(FROM_EMAIL, PASSWORD)
    print(f"[*] Logging in: {status_code} {response}")

    smtp.sendmail(FROM_EMAIL, TO_EMAIL, message.as_string())
    smtp.quit()

dashboard.bind(app)

if __name__ == '__main__':
    app.run(debug=True)
