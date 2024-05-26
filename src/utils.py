import plotly.express as px
import numpy as np

from flask import current_app as app 

import plotly.express as px


def create_figure(data):
    try:
        fig_map = px.scatter_mapbox(
            data,
            lat="lat",
            lon="lon",
            color="traffic",  
            color_discrete_map={'freeFlow':'green', 'heavy':'orange', 'congested':'red'},
            zoom=10,
            height=500,
            mapbox_style="carto-positron",  
            title="Traffic en temps réel"    # Titre ajouté lors de la création de la figure
        )
        fig_map.update_layout(
            margin={"r": 1, "t": 150, "l": 1, "b": 1}
        )
        return fig_map
    except Exception as e:
        app.logger.error("Error creating figure: %s", str(e))
        raise
    

def prediction_from_model(model, hour_to_predict):

    input_pred = np.array([0]*24)
    input_pred[int(hour_to_predict)] = 1

    cat_predict = np.argmax(model.predict(np.array([input_pred])))

    return cat_predict
