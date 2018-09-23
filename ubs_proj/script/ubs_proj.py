import sys, os
import pandas as pd 
import numpy as np 
import json
  
def calc_eod_pos(x):    
    if(x['AccountType'] == 'E'):
        qty = int(x['Quantity'] + x['TransactionQuantityDir'])
    elif(x['AccountType'] == 'I'):
        qty = x['Quantity'] - x['TransactionQuantityDir']
    return qty
            
def assign_direction(x):
    
    if x['TransactionType'] == 'S':
        TransactionQuantityDir = - x['TransactionQuantity']
    elif x['TransactionType'] == 'B':
        TransactionQuantityDir = x['TransactionQuantity']
    return TransactionQuantityDir

def main():

    start_day_df = pd.read_csv('C:/AT_Data/AT/Python_Workspace/Own/ubs_proj/data/in/Input_StartOfDay_Positions.txt')
 
    with open("C:/AT_Data/AT/Python_Workspace/Own/ubs_proj/data/in/1537277231233_Input_Transactions.txt") as datafile:
        tranx_json = json.load(datafile)
    tranx_df = pd.DataFrame(tranx_json)

    tranx_df_agg = tranx_df.groupby(['Instrument','TransactionType'],as_index=False)['TransactionQuantity'].agg(np.sum)

    tranx_df_agg['TransactionQuantityDir'] = tranx_df_agg.apply(lambda x : assign_direction(x), axis=1)
 
    tranx_df_agg1 = tranx_df_agg.groupby(['Instrument'],as_index=False)['TransactionQuantityDir'].agg(np.sum)

    result = pd.merge(start_day_df, tranx_df_agg1, how='left', on='Instrument')
    
    result['TransactionQuantityDir'] = result['TransactionQuantityDir'].apply(lambda x: 0 if pd.isnull(x) else x)

    result.TransactionQuantityDir = result.TransactionQuantityDir.astype(int)

    result['Quantity_EOD'] = result.apply(lambda x : calc_eod_pos(x), axis=1)

    result['Delta'] = result['Quantity_EOD'] - result['Quantity']

    result = result[['Instrument','Account','AccountType','Quantity_EOD','Delta']]

    result.to_csv('C:/AT_Data/AT/Python_Workspace/Own/ubs_proj/data/out/Calculated_EndOfDay_Positions.txt',index=False)
    
    print('Program completed successfully.')
    
if __name__ == "__main__":
    main()

