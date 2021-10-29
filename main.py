# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import base64
import dateutil
import mysql.connector as sql
import os
import pandas as pd
import streamlit as st
import pymysql.cursors
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

sql_query = [
    "SELECT MemNum, COT_Pay_SSA_IT, COT_Balance_CB FROM Curr_Accounts_2021_04_Member",
    "SELECT MemNum, COT_Pay_SSA_IT, COT_Balance_CB FROM Curr_Accounts_2021_05_Member",
    "SELECT MemNum, COT_Pay_SSA_IT, COT_Balance_CB FROM Curr_Accounts_2021_06_Member",
    "SELECT MemNum, COT_Pay_SSA_IT, COT_Balance_CB FROM Curr_Accounts_2021_07_Member",
    "SELECT MemNum, COT_Pay_SSA_IT, COT_Balance_CB FROM Curr_Accounts_2021_08_Member",
    "SELECT MemNum, COT_Pay_SSA_IT, COT_Balance_CB FROM Curr_Accounts_2021_09_Member",
    "SELECT MemNum, COT_Pay_SSA_IT, COT_Balance_CB FROM Curr_Accounts_2021_10_Member",
]

pd.set_option('display.float_format', '{:.2f}'.format)

selected_mnth = st.selectbox('Select the Month', (4, 5, 6, 7, 8, 9, 10))#('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September'))

st.title("COT REPAY JLG")

JLG_Data_Table = 'Curr_JLG_JLG'

conn = sql.connect(host=db_config['hostname'], port=db_config['port'], user=db_config['username'], password=db_config['password'], database=db_config['database'])



Member_Data = pd.read_sql(f"SELECT MemNum, FieldOfficer, BranchName, Community FROM Curr_User_Member",
                                  conn)

JLG_Data_Table = pd.read_sql(f"SELECT MemNum, Date_Disbursement, LoanAmount, COT_Pay_JLG, Disb_AmountToTransfer, Mem_Pay_JLG, SSA_Pay_JLG FROM Curr_JLG_JLG",
                                  conn)

Collections_Table = pd.read_sql(f"SELECT MemNum, Date, Amount, transactionType FROM N_Transaction where transactionType = 'Account_SSA_Deposit'", conn)



Account_Detail = pd.merge(Member_Data, JLG_Data_Table, on = "MemNum", how = "right")

Account_Detail['COT_Pay_JLG']= Account_Detail['COT_Pay_JLG'].astype(float)

Account_Detail['Month_Disbursement']= pd.DatetimeIndex(Account_Detail['Date_Disbursement']).month

Account_Detail['Month_Disbursement_Int'] = Account_Detail['Month_Disbursement'].astype(int)

table = pd.pivot_table(Account_Detail[Account_Detail['Month_Disbursement_Int'] == selected_mnth], columns= ['BranchName'], values= 'COT_Pay_JLG', margins= False, fill_value=0, aggfunc= 'sum')

table['TotalCOTRepay'] = table[table.columns].sum(axis=1)

table['TotalCOTRepay'] = table['TotalCOTRepay'].round(2)

Cot_Repay_JLG = table.transpose()

Account_Detail['Disbursement']= Account_Detail['LoanAmount'].astype(float)

table2 = pd.pivot_table(Account_Detail[Account_Detail['Month_Disbursement_Int'] == selected_mnth], columns= ['BranchName'], values= 'Disbursement', margins= False, fill_value=0, aggfunc= 'sum')

table2['TotalDisbursement'] = table2[table2.columns].sum(axis=1)

Disb_Table = table2.transpose()

df_new = pd.concat([Cot_Repay_JLG, Disb_Table], join = 'inner', axis = 1)

df_new['RepaymentPercent'] = Cot_Repay_JLG['COT_Pay_JLG']/Disb_Table['Disbursement'] * 100

df_new.loc['Total'] = df_new.sum()

df_new.loc['Total'].at['RepaymentPercent'] = df_new.loc['Total'].at['COT_Pay_JLG']/df_new.loc['Total'].at['Disbursement'] * 100

df_new = df_new.astype('int64')

st.table(df_new)

st.title("SSA Collections")

Account_Detail_Collections = pd.merge(Member_Data, Collections_Table, on = "MemNum", how = "right")

Account_Detail_Collections['Month_Disbursement']= pd.DatetimeIndex(Account_Detail_Collections['Date']).month

Account_Detail_Collections['Month_Disbursement_Int'] = Account_Detail_Collections['Month_Disbursement'].astype(int)

table = pd.pivot_table(Account_Detail_Collections[Account_Detail_Collections['Month_Disbursement_Int'] == selected_mnth], columns= ['BranchName'], values= 'Amount', margins= False, fill_value=0, aggfunc= 'sum')

table['TotalCollections'] = table[table.columns].sum(axis=1)

st.table(table)

st.title("COT Repay SSA and Closing Balance")

curr = conn.cursor()

query_mnth = sql_query[selected_mnth - 4]

Collections_Table_COT_Repay_SSA = pd.read_sql(query_mnth, conn)
#curr.execute(query_mnth)

#print(query_mnth)

Account_Detail_COT_Repay = pd.merge(Member_Data, Collections_Table_COT_Repay_SSA, on = "MemNum", how = "right")

Account_Detail_COT_Repay['COT_Pay_SSA_IT']= Account_Detail_COT_Repay['COT_Pay_SSA_IT'].astype(float)

Account_Detail_COT_Repay['COT_Pay_SSA_IT']= Account_Detail_COT_Repay['COT_Pay_SSA_IT'].round(2)

Account_Detail_COT_Repay['COT_Balance_CB']= Account_Detail_COT_Repay['COT_Balance_CB'].astype(float)

Account_Detail_COT_Repay['COT_Balance_CB']= Account_Detail_COT_Repay['COT_Balance_CB'].round(2)

table2 = pd.pivot_table(Account_Detail_COT_Repay, columns= ['BranchName'], values= ['COT_Pay_SSA_IT', 'COT_Balance_CB'], margins= False, fill_value=0, aggfunc= 'sum')

table2['TotalCollections'] = table2[table2.columns].sum(axis=1)

st.table(table2)

conn.close()