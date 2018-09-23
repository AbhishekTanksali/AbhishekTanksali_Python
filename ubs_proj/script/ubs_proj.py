
'''
python ubs_proj.py arg_1 arg_2 arg_3 arg_4

arg_1 => Input start of day postions file path
arg_2 => Input transactions file path
arg_3 => Output calculated end of day transaction file path
arg_4 => Input expected end of day transaction file path

Example: 
    python ubs_proj.py  C:/AT_Data/AT/Python_Workspace/Own/ubs_proj/data/in/Input_StartOfDay_Positions.txt \
                        C:/AT_Data/AT/Python_Workspace/Own/ubs_proj/data/in/1537277231233_Input_Transactions.txt \
                        C:/AT_Data/AT/Python_Workspace/Own/ubs_proj/data/out/Calculated_EndOfDay_Positions.txt \
                        C:/AT_Data/AT/Python_Workspace/Own/ubs_proj/data/in/Expected_EndOfDay_Positions.txt
                        
## python ubs_proj.py C:/AT_Data/AT/Python_Workspace/Own/ubs_proj/data/in/Input_StartOfDay_Positions.txt C:/AT_Data/AT/Python_Workspace/Own/ubs_proj/data/in/1537277231233_Input_Transactions.txt C:/AT_Data/AT/Python_Workspace/Own/ubs_proj/data/out/Calculated_EndOfDay_Positions.txt C:/AT_Data/AT/Python_Workspace/Own/ubs_proj/data/in/Expected_EndOfDay_Positions.txt
'''

import sys, os
import pandas as pd 
import numpy as np 
import json
  
## Function to calculate end of day positions
def calc_eod_pos(x):    
    if(x['AccountType'] == 'E'):
        qty = int(x['Quantity'] + x['TransactionQuantityDir'])
    elif(x['AccountType'] == 'I'):
        qty = x['Quantity'] - x['TransactionQuantityDir']
    return qty
 
## Function to assign trade direction           
def assign_direction(x):
    
    if x['TransactionType'] == 'S':
        TransactionQuantityDir = - x['TransactionQuantity']
    elif x['TransactionType'] == 'B':
        TransactionQuantityDir = x['TransactionQuantity']
    return TransactionQuantityDir

## main function where programe execution starts
def main():

    #positions_file = 'C:/AT_Data/AT/Python_Workspace/Own/ubs_proj/data/in/Input_StartOfDay_Positions.txt'
    positions_file = sys.argv[1]
    
    try:      
        start_day_df = pd.read_csv(positions_file)      
    except Exception as e:
        print("Error opening positions file.\n"+str(e))
        sys.exit()
        
    #transaction_file = "C:/AT_Data/AT/Python_Workspace/Own/ubs_proj/data/in/1537277231233_Input_Transactions.txt"
    transaction_file = sys.argv[2] 
    
    try:
        with open(transaction_file) as datafile:
            tranx_json = json.load(datafile)
            
    except Exception as e:
        print("Error opening transaction file.\n"+str(e))
        sys.exit()
        
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
    
    result.rename(columns={'Quantity_EOD': 'Quantity'}, inplace=True)
    
    print('\n*****************************************************')
    print('                End of Day positions                 ')
    print('*****************************************************\n')
    print(result)
    print('*****************************************************\n')
    
    #out_file = 'C:/AT_Data/AT/Python_Workspace/Own/ubs_proj/data/out/Calculated_EndOfDay_Positions.txt'
    out_file = sys.argv[3]
    
    result.to_csv(out_file, index=False)    
    
    
    ## Unit Testing
    #expected_eod_txn = 'C:/AT_Data/AT/Python_Workspace/Own/ubs_proj/data/in/Expected_EndOfDay_Positions.txt'
    expected_eod_txn = sys.argv[4]
    try:
        end_day_df = pd.read_csv(expected_eod_txn)      
    except Exception as e:
        print("Error opening end of day positions file.\n"+str(e))
        sys.exit()
    
    try:
        pd.testing.assert_frame_equal(end_day_df,result)
    except Exception as e:
        print("Assertion error \n\n"+str(e))
        sys.exit()
    
    
    print('Program completed successfully.')
    
if __name__ == "__main__":
    main()

