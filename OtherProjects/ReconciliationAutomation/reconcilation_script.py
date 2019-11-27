import time
start_time = time.time()
import pandas as pd
import numpy as np
import logging 

logging.basicConfig(filename="../Logs/logFile.log", format='%(asctime)s %(message)s', filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.INFO)

logger.info('############################## Execution Started ##############################')
print('############################## Execution Started ##############################')
print('Check logs in ../Logs/logFile.log to see script progress')
logger.info('-----------Starting execution for Comment generation based on Native Amount difference.-------------')

logger.info('Reading files started...')

start = time.time()

logger.info('Reading Glass Recon File.')
glassRecon_df = pd.read_excel(r'../Input Data/GlassRecon.xlsx')
# df = pd.read_csv(r'../FinalData/Glass Recon BD9.csv', dtype='unicode')

logger.info('Reading Global Account List File.')
globalAccount_df = pd.read_csv(r'../Input Data/GlobalAccountList.csv')

logger.info('Reading Star-GL rec File.')
starGLRec_df = pd.read_excel(r'../Input Data/StarGLRec.xlsx')

logger.info('Reading Customer Counter Party mapping file.')
globalCPTY_df = pd.read_excel(r'../Input Data/GlobalCPTYMapping.xlsx')

message = 'Time taken to read all files: ' + str(round((time.time() - start) / 60, 2)) + ' minutes.'
logger.info(message)

glassRec_df = glassRecon_df.copy()

def update_LE(row):
    """
    Function to extract Legal Entity information from Key column. 
    Input: Key value
    Return: Legal Entity String
    """
    key_split_list = [x.strip() for x in row.split('-')]
    return key_split_list[1]

def update_Account(row):
    """
    Function to extract Account information from Key column. 
    Input: Key value
    Return: Account String
    """
    key_split_list = [x.strip() for x in row.split('-')]
    return key_split_list[2]

def vlookup(value, list_obj):
    """
    Function similar to VLOOKUP()
    Input: Value to look for, List to Look At
    Output: Yes if value is available, No if not available.
    """
    if value in list_obj:
        return 'Yes'
    else:
        return 'No'

def getKey(legalEntity, account, department, nativeCurrency):
    """
    Function used to create unique key from input
    Input : Legal Entity, Account, Department, Native Currency
    Output: Unique key generated from Input
    """
    val = str(legalEntity) + str(account) + str(department) + str(nativeCurrency)
    return str(val)

def getNatvAmount(exist, ukey):
    """
    Function used to get Native Amount - Ledger value associated for particular Unique key 
    from Star-GL recon file.
    Input: Existance status, Unique key
    Output: Associated Native Amount - Ledger float value.
    """
    if exist == 'Yes':
        return float(sglRecPivot_df[sglRecPivot_df['UniqueKeyP2'] == ukey]['Native Amount - Ledger'])
    elif exist == 'No':
        return np.nan

def getDifference(val1, val2):
    """
    Function to get the difference between Natv Amount and Native Amount - Ledger
    Input: float value of Natv Amount and float value of Native Amount - Ledger
    Output: Difference in float.
    """
    val = float(val1) - float(val2)
    return float(val)

def addComment(difference):
    """
    Function to add comment based on difference value.
    Input: Difference value in float
    Output: Associated comment.
    """
    if abs(difference) == 0.0:
        return 'Good to Post'
    elif abs(difference) < 100.0:
        return 'Less than $100'
    else:
        return 'More than $100'

def getComment(exist, ukey):
    """
    Function to get Comment value for associated UniqueKey of Pivot-1
    Input: Existance status of UniqueKey, Unique Key
    Output: Comment value
    """
    if exist == 'Yes':
        return str(glRecPivot_df[glRecPivot_df['UniqueKeyP1'] == ukey]['Comment'].reset_index(drop=True)[0])
    elif exist == 'No':
        return np.nan

def getCounterpartyId(exist, CustomerAccountId):
    """
    Function to get CounterpartyId for accociated CustomerAccountId from Customer - Counterparty dataframe
    Input: Existance status of Customer #, CustomerAccountId
    Output: CounterpartyId
    """
    if exist == 'Yes':
        return str(globalCPTY_df[globalCPTY_df['CustomerAccountId'] == CustomerAccountId]['CounterpartyId'])
    elif exist == 'No':
        return np.nan

logger.info('Removing leading and trailing spaces from column names from Glass Recon file.')
glassRec_df.columns = glassRec_df.columns.str.strip()

logger.info('Adding new column *LEntity* in Glass Recon file which contains Legal Entity.')
glassRec_df['LEntity'] = glassRec_df.apply(lambda row : update_LE(row['Key']), axis = 1)

logger.info('Adding new column *Account* in Glass Recon file which contains Account information.')
glassRec_df['Account'] = glassRec_df.apply(lambda row : update_Account(row['Key']), axis = 1)

logger.info('Removing spaces and/or replacing blank values with NAV in Desk column.')
glassRec_df.Desk = glassRec_df.Desk.replace(r'^\s*$', 'NAV', regex=True)

logger.info('Creating new column Department which is copied from Desk.')
glassRec_df['Department'] = glassRec_df['Desk']

logger.info('Creating list of Unique GL A/C.')
account_list = (list(globalAccount_df['GL A/C.']))

logger.info('Checking whether the Glass Recon Account is available in Unique GL A/C. list.')
glassRec_df['isAccoutInList'] = glassRec_df.apply(lambda row : vlookup(row['Account'], account_list), axis=1)

logger.info('Removing records whose Account is not available in Unique GL A/C. list.')
glassRec_df.drop(glassRec_df[glassRec_df['isAccoutInList'] == 'No'].index, inplace = True)

logger.info('Removing leading and trailing spaces from column names of Star-GL rec file.')
starGLRec_df.columns = starGLRec_df.columns.str.strip()

logger.info('Creating a list of unique GL Account Number from Star-GL rec file.')
gl_accountUnique_list = list(set(starGLRec_df['GL Account Number']))

logger.info('Checking whether the Account in Glass recon file is present in Star-GL file or not.')
glassRec_df['isAccInF3'] = glassRec_df.apply(lambda row : vlookup(row['Account'], gl_accountUnique_list), axis=1)

logger.info('Removing the records from Glass recon file whose Account is not present in Star-GL rec file.')
glassRec_df.drop(glassRec_df[glassRec_df['isAccInF3'] == 'No'].index, inplace = True)

logger.info('Dropping the records from Glass recon file whose Item Descr is GL Balance.')
glassRec_df.drop(glassRec_df[glassRec_df['Item Descr'] == 'GL Balance'].index, inplace = True)

glassRec_df = glassRec_df.reset_index(drop=True)
starGLRec_df = starGLRec_df.reset_index(drop=True)

logger.info('Generating unique key for Glass recon file.')
glassRec_df['UniqueKeyF1'] = glassRec_df.apply(lambda row : getKey(row['LEntity'], row['Account'], row['Desk'], row['CCY']), axis = 1)

logger.info('Generating unique key for Star-GL rec file.')
starGLRec_df['UniqueKeyF3'] = starGLRec_df.apply(lambda row : getKey(row['Legal Entity ID'], row['GL Account Number'], 
                                                       row['Department ID'], row['Native Currency']), axis = 1)

logger.info('Creating pivot table from Glass recon file : Pivot-1')
glRecPivot_df = pd.DataFrame(pd.pivot_table(glassRec_df, index = ['LEntity', 'Account', 'Desk', 'CCY'], 
              values = ['Natv Amount'], aggfunc = np.sum, fill_value=0).reset_index())

logger.info('Generating unique key for Pivot-1.')
glRecPivot_df['UniqueKeyP1'] = glRecPivot_df.apply(lambda row : getKey(row['LEntity'], row['Account'], 
                                                                       row['Desk'], row['CCY']), axis = 1)

logger.info('Creating pivot table from Star-GL rec file : Pivot-2.')
sglRecPivot_df = pd.DataFrame(pd.pivot_table(starGLRec_df, index = ['Legal Entity ID', 'GL Account Number', 
                                                                    'Department ID', 'Native Currency'], 
              values = ['Native Amount - Ledger'], aggfunc = np.sum, fill_value=0).reset_index())

logger.info('Generating unique key for Star-GL rec pivot table.')
sglRecPivot_df['UniqueKeyP2'] = sglRecPivot_df.apply(lambda row : getKey(row['Legal Entity ID'], row['GL Account Number'], 
                                                       row['Department ID'], row['Native Currency']), axis = 1)

logger.info('Creating a list of unique UniqueKeys from Pivot-2.')
uniquekey_pivot2_list = list(set(sglRecPivot_df['UniqueKeyP2']))

logger.info('Checking whether the unique keys from Pivot-1 are present in Pivot-2 or not.')
glRecPivot_df['isUKP1InP2'] = glRecPivot_df.apply(lambda row : vlookup(row['UniqueKeyP1'], uniquekey_pivot2_list), axis=1)

logger.info('Adding column containing Native Amount - Ledger value for associated Unique key in Pivot-1')
glRecPivot_df['Native Amount - Ledger'] = glRecPivot_df.apply(lambda row : getNatvAmount(row['isUKP1InP2'], row['UniqueKeyP1']), axis = 1)

logger.info('Adding column containing difference between Natv Amount and Native Amount - Ledger')
glRecPivot_df['Difference'] = glRecPivot_df.apply(lambda row : getDifference(row['Natv Amount'], row['Native Amount - Ledger']), axis = 1)

logger.info('Rounding off the difference values.')
glRecPivot_df.Difference = glRecPivot_df.Difference.round()

logger.info('Adding comments against each record in Pivot-1.')
glRecPivot_df['Comment'] = glRecPivot_df.apply(lambda row : addComment(row['Difference']), axis = 1)

logger.info('Creating dataframe of records whose difference is out of Scope / NaN from Glass recon file.')
outOfScope_GLRec_df = glRecPivot_df[glRecPivot_df['Comment'].isnull()][['LEntity', 'Account', 'Desk', 'CCY', 'UniqueKeyP1']]

logger.info('Creating a list of unique UniqueKeys from Pivot-1.')
uniquekey_pivot1_list = list(set(glRecPivot_df.UniqueKeyP1))

logger.info('Checking whether the UniqueKey of Glass recon present in Pivot-1 or not.')
glassRec_df['isFound'] = glassRec_df.apply(lambda row : vlookup(row['UniqueKeyF1'], uniquekey_pivot1_list), axis=1)

logger.info('Checking whether the UniqueKey of Star-GL rec present in Pivot-1 or not.')
starGLRec_df['isFound'] = starGLRec_df.apply(lambda row : vlookup(row['UniqueKeyF3'], uniquekey_pivot1_list), axis=1)

logger.info('Adding comment column in Glass recon file.')
glassRec_df['Comment'] = glassRec_df.apply(lambda row : getComment(row['isFound'], row['UniqueKeyF1']), axis = 1)

logger.info('Adding comment column in Glass recon file.')
starGLRec_df['Comment'] = starGLRec_df.apply(lambda row : getComment(row['isFound'], row['UniqueKeyF3']), axis = 1)

logger.info('-----------Starting execution for Customer - CounterpartyId mapping.-------------')

logger.info('Converting Customer # column data type to string.')
glassRec_df['Customer #'] = glassRec_df['Customer #'].astype(str)

logger.info('Converting CustomerAccountId column data type to string.')
globalCPTY_df['CustomerAccountId'] = globalCPTY_df['CustomerAccountId'].astype(str)

logger.info('Converting CounterpartyId column data type to string.')
globalCPTY_df['CounterpartyId'] = globalCPTY_df['CounterpartyId'].astype(str)

logger.info('Removing leading and trailing spaces from each record of Customer # column from Glass recon file.')
glassRec_df['Customer #'] = glassRec_df['Customer #'].str.strip()

logger.info('Dropping duplicate records from Customer - Counterparty dataframe')
globalCPTY_df.drop_duplicates(keep=False, inplace = True)

logger.info('Creating list of unique CustomerAccountId from Customer - Counterparty dataframe')
customerAccountId_list = list(set(globalCPTY_df['CustomerAccountId']))

logger.info('Checking whether the Customer # is present in Customer - Counterparty dataframe or not.')
glassRec_df['isCustFound'] = glassRec_df.apply(lambda row : vlookup(row['Customer #'], customerAccountId_list), axis=1)

logger.info('Adding column CounterpartyId for associated Customer # in Glass recon file.')
glassRec_df['CounterpartyId'] = glassRec_df.apply(lambda row : getCounterpartyId(row['isCustFound'], row['Customer #']), axis = 1)

logger.info('Dropping unnecessary columns from Glass recon file.')
glassRec_df = glassRec_df.drop(['isAccoutInList', 'isAccInF3', 'UniqueKeyF1', 'isFound', 'isCustFound'], axis = 1)

logger.info('Dropping unnecessary columns from Star-GL rec file.')
starGLRec_df = starGLRec_df.drop(['UniqueKeyF3', 'isFound'], axis = 1)

logger.info('Writing final results of Glass recon file as : FinalResults_GlassRecon.xlsx')
glassRec_df.to_excel(r'../Output Data/FinalResults_GlassRecon.xlsx', index = False)

logger.info('Writing final results of Star-GL rec file as : FinalResults_StarGLRec.xlsx')
starGLRec_df.to_excel(r'../Output Data/FinalResults_StarGLRec.xlsx', index = False)

logger.info('############################## Execution Finished ##############################')
message = "Time taken to execute the script: " + str(round((time.time() - start_time) / 60, 2)) + ' minutes.'
logger.info(message)