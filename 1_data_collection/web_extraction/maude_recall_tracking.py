"""
Created on Tue Apr 14 11:25:06 2020
@author: thanhng
"""

import pandas as pd
import numpy as np
import os
import glob
import data_cleaning

#########################

sorted_data = pd.read_csv('data_recall_1819.csv')

#*********************************************
#count number of reports for each dataset

#tracking_df = pd.read_csv('tracking_1819.csv')


tracking_df = CREATE_TRACKING_DF(sorted_data)


#count missing in event_type
tracking_df['missing_in_AE'] = 'none'
tracking_df['missing_event_date'] = 'none'
tracking_df['missing_event_type'] = 'none'

tracking_df = COUNT_MISSING(sorted_data, tracking_df)


### COUNT # of deaths, malfunction, injury

tracking_df['#_of_malfunction'] = 0
tracking_df['#_of_injury'] = 0
tracking_df['#_of_death'] = 0

tracking_df = COUNT_EVENT_TYPE(sorted_data, tracking_df)

tracking_df['missing_event_type'] = tracking_df['counts_in_maude']
								- tracking_df[['#_of_malfunction','#_of_injury', '#_of_death']].sum(axis = 1)
##count AE
tracking_df['#_of_AE'] = 'none'
tracking_df = COUNT_AE(sorted_data, tracking_df)

####get the first malf, injury, death
tracking_df['first_malfunction'] = 'none'
tracking_df['first_injury'] = 'none'
tracking_df['first_death'] = 'none'

tracking_df = GET_FIRST_EVENT_TYPE(sorted_data, tracking_df)


#MAUDE FIRST DATE
tracking_df = GET_FIRST_DATE(sorted_data, tracking_df)


#date diff


def REMOVE_MALF(data):
    #extract data
    inj=data[data['event_type']!='Malfunction']
    #print results
    inj_MEAN = inj['date_of_event_edit'].diff().mean().days
    inj_MEDIAN = inj['date_of_event_edit'].diff().median().days
    return inj_MEAN, inj_MEDIAN


tracking_df['mean_date_diff_bw_event'] = '0'
tracking_df['median_date_diff_bw_event'] = '0'

tracking_df['mean_date_diff_bw_deathinj'] = '0'
tracking_df['median_date_diff_bw_deathinj'] = '0'


sorted_data['date_diff'] = 'none'

sorted_data['date_of_event_edit'] = CONVERT_COLUMN_TO_DATETIME(sorted_data, 'date_of_event')


for name in dataset_name:
    df_index = sorted_data.loc[group_dataset.groups.get(name)].index
    sorted_data.loc[df_index, 'date_diff']= sorted_data.loc[df_index, 'date_of_event_edit'].diff()
    diff_col = sorted_data_df.loc[df_index, 'date_diff']
    diff_MEAN = diff_col.mean().days
    diff_MEDIAN = diff_col.median().days

    tracking_df.loc[group_tracking.groups.get(name),'mean_date_diff_bw_event'] = diff_MEAN
    tracking_df.loc[group_tracking.groups.get(name), 'median_date_diff_bw_event'] = diff_MEDIAN

    df = sorted_data_df.loc[df_index]
    inj_MEAN, inj_MEDIAN = REMOVE_MALF(df)

    tracking_df.loc[group_tracking.groups.get(name),'mean_date_diff_bw_deathinj'] = inj_MEAN
    tracking_df.loc[group_tracking.groups.get(name), 'median_date_diff_bw_deathinj'] = inj_MEDIAN


#EXPORT TRACKING DF
tracking_df.to_csv('tracking_18.csv', index = False)


###recall_Website

from datetime import datetime
data = pd.read_csv('recall_web_2018.csv')

data['dataset'] = data['dataset'].str.lower()
data = data.sort_values('dataset')


data['recall_date'] = pd.to_datetime(data.recall_date)

data['recall_date'] = data['recall_date'].dt.strftime('%Y%m%d')

tracking_df = pd.read_csv('tracking.csv')

merge = pd.merge(data, tracking_df, on='dataset')

merge.to_csv('tracking_18.csv', index = False)



complete_19 = pd.read_csv('complete_recall_2019.csv')


combine = pd.concat([merge, complete_19])

combine.to_csv('recall_tracking_1819.csv', index = False)


#MAUDE FIRST AE
tracking_df['#_events_from_1st_event_to_1st_AE'] = 'none'


count =0
for (name, index) in zip(dataset_name, range(tracking_df.shape[0])):

   df = sorted_data.loc[group_dataset.groups.get(name)].reset_index()
   AE_first = df['adverse_event_flag'][0]
   if AE_first == 'Y':
       tracking_df.loc[index, '#_events_from_1st_event_to_1st_AE'] = 0
   if AE_first == 'N':
        index_df = pd.DataFrame(df.groupby(['adverse_event_flag']).first()['index'])
        index_trans = index_df.transpose()
        if len(index_trans.columns) == 1:
           tracking_df.loc[index, '#_events_from_1st_event_to_1st_AE'] = 0
        if len(index_trans.columns) > 1:
            res = index_trans['Y'].values - index_trans['N'].values
            tracking_df.loc[index,  '#_events_from_1st_event_to_1st_AE'] = res


#######
### '#_malf_before_1st_AE'

sorted_data = pd.read_csv('data_recall_1819.csv')

tracking_df = pd.read_csv('tracking_1819.csv')


count =0
for (name, index) in zip(dataset_names, range(tracking_df.shape[0])):

    df = sorted_data.loc[group_dataset.groups.get(name)].reset_index()
    index_df = pd.DataFrame(df.groupby(['event_type']).first()['index'])
    index_trans = index_df.transpose()

    if len(index_trans.columns)==1:
        if 'Injury' not in index_trans.columns.values:
            tracking_df.loc[index, '#_malf_before_1st_AE'] = 'none'

    if len(index_trans.columns) == 2:
        if 'Death' not in index_trans.columns.values:
          res = index_trans['Injury'].values - index_trans['Malfunction'].values
          tracking_df.loc[index, '#_malf_before_1st_AE'] = res

    if len(index_trans.columns) ==3:

        check_min = index_trans.idxmin(axis = 1).values
        if check_min == 'Malfunction':
            if (index_trans['Injury'].values - index_trans['Death'].values) <0:
                res = index_trans['Injury'].values - index_trans['Malfunction'].values
                tracking_df.loc[index, '#_malf_before_1st_AE'] = res

            if (index_trans['Injury'].values - index_trans['Death'].values) >0:
                res = index_trans['Death'].values - index_trans['Malfunction'].values
                tracking_df.loc[index, '#_malf_before_1st_AE'] = res

        if check_min !='Malfunction':
            res = index_trans.min(axis = 1) - index_trans['Malfunction'].values
            tracking_df.loc[index, '#_malf_before_1st_AE'] = res.values

######

track_original = pd.read_csv('tracking_1819.csv')


fil = track_original.filter(['dataset', 'date_firm_initiated_recall', 'recall_date'])

fil_1 = tracking_df.filter(['dataset', 'first_malfunction', 'first_injury', 'first_death'])

#subtract date, recall - 1st_malf
merge = pd.merge(fil, fil_1, on='dataset')


#fix bug, remove .0 in date

column_convert = ['recall_date', 'first_malfunction', 'first_injury', 'first_death']

column_being_subtracted = column_convert[1:]

def REMOVE_FLOAT(data, column):
    for i in range(data.shape[0]):
        data.loc[i, column] = str(data.loc[i, column]).replace('.0', '')
        return data[column]

for col in column_being_subtracted:
    REMOVE_FLOAT(merge, col)


#convert column to datetime object

def CONVERT_COLUMN_TO_DATETIME(data, column):
    data[column] = pd.to_datetime(data[column], format='%Y%m%d', errors='coerce')
    return data[column]

for col in column_convert:
    merge[col] = CONVERT_COLUMN_TO_DATETIME(merge, col)

column_different = ['recall-malf', 'recall-injury', 'recall-death']
column_being_subtracted = column_convert[1:]


def DATE_DIFFERENT(data, col1, col2, col_result):
    data[col_result] = (data[col1] - data[col2]).dt.days
    return data[col_result]


for (col_res,col_subtract)  in zip(column_different, column_being_subtracted):
    merge[col_res] =  DATE_DIFFERENT(merge, 'recall_date', col_subtract, col_res)/365


merge.filter(column_different).describe()


'''on average, it takes 5 years from the first death event to recall date
7 years from first injury to recall date
8 years from first malfunction to recall date '''

def GET_THE_MAX_ROW(data, col):
    return data.loc[data[col].idxmax()]

GET_THE_MAX_ROW(merge, 'recall-malf')


#GET MAX OF EVEVRY ROWS
np.mean(merge.filter(column_different).max(axis = 1))


np.mean(merge.filter(column_different).min(axis = 1))

merge.to_csv('date_different_to_recall.csv', index = False)
