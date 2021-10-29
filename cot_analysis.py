# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import base64
import dateutil
import mysql.connector as sql
import os
import pandas as pd
import streamlit as st
import array as arr
import ruamel.yaml as yaml
import lib
import deetly as dl
import numpy as np



db_config = dict([
    ('hostname', 'canvasdb.caxvr8jox9y6.us-east-2.rds.amazonaws.com'),
    ('port', 3306),
    ('username', 'admin'),
    ('password', '77YnH0bqO8oHMYZGmu78'),
    ('database', 'Vriddhi')
])


DATA_DIR = 'DataFiles'

pd.set_option('display.float_format', '{:.2f}'.format)

selected_mnth = st.selectbox('Select the Month', (1, 2, 3, 4, 5, 6, 7, 8, 9))

Member_Data = pd.read_sql(f"SELECT MemNum, FieldOfficer, BranchName, Community FROM Curr_User_Member",
                                  conn)

COT_Data_Table = pd.read_sql(f"SELECT MemNum, COT_Balance_CB, COT_Total_OD, COT_Due, COT_Due_IB, COT_IntOD_CB FROM Curr_Accounts_2021_09_Member",
                                  conn)

Account_Detail = pd.merge(Member_Data, COT_Data_Table, on = "MemNum", how = "right")

COT_analysis_table = pd.pivot_table(Account_Detail[Account_Detail['Month_Disbursement_Int'] == selected_mnth], columns= ['BranchName'], values= 'COT_Balance_CB', margins= False, fill_value=0, aggfunc= 'sum')

st.table(COT_analysis_table)
