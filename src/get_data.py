import pandas as pd
import requests

class GetData(object):

    def __init__(self, url) -> None:
        self.url = url

        response = requests.get(self.url)
        self.data = response.json()

    def processing_one_point(self, data_dict: dict):

        temp = pd.DataFrame({key:[data_dict[key]] for key in ['datetime', 'geo_point_2d', 'averagevehiclespeed', 'traveltime', 'trafficstatus']})
        #modification supprimé traffic_status
        temp = temp.rename(columns={'trafficstatus':'traffic'})
        #modification de la clé
        temp['lat'] = temp.geo_point_2d.map(lambda x : x['lat'])
        temp['lon'] = temp.geo_point_2d.map(lambda x : x['lon'])
        #modification de latitude en lat et longitude en lon
        del temp['geo_point_2d']

        return temp

    def __call__(self):

        res_df = pd.DataFrame({})

        for data_dict in self.data:
            temp_df = self.processing_one_point(data_dict)
            res_df = pd.concat([res_df, temp_df])
        #reprise de l'indentation
        
        res_df = res_df[res_df.traffic != 'unknown']
        #correction de syntaxe fermeture []
        return res_df