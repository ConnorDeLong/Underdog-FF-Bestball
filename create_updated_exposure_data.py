# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 18:12:14 2021

@author: conde
"""

import pandas as pd
from datetime import datetime

adp_data_path = r'C:\Users\conde\OneDrive\Documents\Python-Projects\Underdog\Data\ADP Data\Underdog_ADP - 2021-08-24.csv'
pick_value_data_path =  r'C:\Users\conde\OneDrive\Documents\Python-Projects\Underdog\Data\Draft Data\PFF Pick Value.csv'
draft_data_path =  r'C:\Users\conde\OneDrive\Documents\Python-Projects\Underdog\Data\Draft Data\All Drafts.csv'

df_adp = pd.read_csv(adp_data_path)
df_pick_value = pd.read_csv(pick_value_data_path)
df_draft = pd.read_csv(draft_data_path)


def clean_initial_draft_data(df_draft):
    
    df = df_draft.copy()
    
    # df['Picked At'] = df[df['Picked At']].str[:10]
    
    df['Picked At'] = df['Picked At'].str[:19]
    df['Pick Datetime'] = pd.to_datetime(df['Picked At'], format="%Y-%m-%d %H:%M:%S")
    
    return df
    

check = clean_initial_draft_data(df_draft)
print(check)



