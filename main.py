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

JLG_STATE_COLUMNS = """COT_Pay_JLG
                      JLG_Disbursement_Tr
                      Mem_Pay_JLG
                      JLG_Pay_SSA
                 """.split()


selected_mnth = st.selectbox('Select the Month', (1, 2, 3, 4, 5, 6, 7, 8, 9))#('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September'))

print(selected_mnth)

st.title("COT REPAY JLG")

JLG_Data_Table = 'Curr_JLG_JLG'

trans_details = JLG_STATE_COLUMNS

conn = sql.connect(host=db_config['hostname'], port=db_config['port'], user=db_config['username'], password=db_config['password'], database=db_config['database'])



Member_Data = pd.read_sql(f"SELECT MemNum, FieldOfficer, BranchName, Community FROM Curr_User_Member",
                                  conn)

JLG_Data_Table = pd.read_sql(f"SELECT MemNum, Date_Disbursement, LoanAmount, COT_Pay_JLG, Disb_AmountToTransfer, Mem_Pay_JLG, SSA_Pay_JLG FROM Curr_JLG_JLG",
                                  conn)

conn.close()

Account_Detail = pd.merge(Member_Data, JLG_Data_Table, on = "MemNum", how = "right")

Account_Detail['COT_Pay_JLG']= Account_Detail['COT_Pay_JLG'].astype(float)

Account_Detail['Month_Disbursement']= pd.DatetimeIndex(Account_Detail['Date_Disbursement']).month

Account_Detail['Month_Disbursement_Int'] = Account_Detail['Month_Disbursement'].astype(int)

table = pd.pivot_table(Account_Detail[Account_Detail['Month_Disbursement_Int'] == selected_mnth], columns= ['BranchName'], values= 'COT_Pay_JLG', margins= False, fill_value=0, aggfunc= 'sum')

table['TotalCOTRepay'] = table[table.columns].sum(axis=1)

Cot_Repay_JLG = table.transpose()

Account_Detail['Disbursement']= Account_Detail['LoanAmount'].astype(float)

table2 = pd.pivot_table(Account_Detail[Account_Detail['Month_Disbursement_Int'] == selected_mnth], columns= ['BranchName'], values= 'Disbursement', margins= False, fill_value=0, aggfunc= 'sum')

table2['TotalDisbursement'] = table2[table2.columns].sum(axis=1)

Disb_Table = table2.transpose()

#print(disb_ratio)

df_new = pd.concat([Cot_Repay_JLG, Disb_Table], join = 'inner', axis = 1)

df_new['RepaymentPercent'] = Cot_Repay_JLG['COT_Pay_JLG']/Disb_Table['Disbursement'] * 100

st.table(df_new)



