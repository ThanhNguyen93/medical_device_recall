
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 14:10:03 2020

@author: thanhng
"""
import os, requests
import pandas as pd
import re, json

################
'''data source: https://open.fda.gov/apis/device/recall/ '''
#################

url = ('https://api.fda.gov/device/recall.json?'
       'api_key=lvmKNeCdZN3OX0QttZL2ovaDsFpLb26J5otfRFRh'
       '&search=event_date_terminated:[2019-01-01+TO+2019-12-31]'
       '+firm_fei_number:"3002808461"'
       '+AND+res_event_number:"84309"'
       '&limit=100')

url = ('https://api.fda.gov/device/recall.json?'
       'api_key=lvmKNeCdZN3OX0QttZL2ovaDsFpLb26J5otfRFRh'
       '&count=res_event_number'
       '&limit=100')

response = requests.get(url).json()

response['meta']

response['results']


def RECALL_API_DF(response):
    res_df = []
    for i in range(len(response['results'])):
        result_dict = response['results'][i]

        device_name = result_dict.get('openfda').get('device_name')
        medical_specialty = result_dict.get('openfda').get('medical_specialty_description')
        device_class = result_dict.get('openfda').get('device_class')
        product_code = result_dict.get('product_code')
        root_cause_description = result_dict.get('root_cause_description')
        event_date_terminated =result_dict.get('event_date_terminated')
        k_number = result_dict.get('k_numbers')
        other_submission = result_dict.get('other_submission_description')
        res_event_number = result_dict.get('res_event_number')
        firm_fei_number = result_dict.get('firm_fei_number')
        product_res_number = result_dict.get('product_res_number')
        pma_numbers = result_dict.get('pma_numbers')

        res_df.append({
                'res_event_number': res_event_number,
                'firm_fei_number': firm_fei_number,
                'k_numbers': k_number,
                'pma_numbers': pma_numbers,
                'device_name': device_name,
                'medical_specialty': medical_specialty,
                'device_class': device_class,
                'product_code': product_code,
                'root_cause_description': root_cause_description,
                 'event_date_terminated':  event_date_terminated,
                 'product_res_number': product_res_number
                })

    df = pd.DataFrame(res_df)
    return df

trial = RECALL_API_DF(response)



#########reinforcement
'''data source: https://open.fda.gov/apis/device/enforcement/ '''
############

def ENFORCEMENT_DF(response):
    res_df = []
    for i in range(len(response['results'])):
        result_dict = response['results'][i]
        res_df.append(result_dict)
    return pd.DataFrame(res_df)


url=('https://api.fda.gov/device/enforcement.json?'
        'api_key=lvmKNeCdZN3OX0QttZL2ovaDsFpLb26J5otfRFRh'
        '&search='
   #     'product_description:"980 ventilator"'
         #'+recall_number:"Z-1208-2018"'
         '+report_date:[20190101+TO+20191231]'
         '&limit=100')


response = requests.get(url).json()

response['meta']

count = ENFORCEMENT_DF(response)


####implement 'skip' to get all data
list_of_data=[]
start = 100
for i in range(229):
    skip = start*i

    url=('https://api.fda.gov/device/enforcement.json?'
            'api_key=lvmKNeCdZN3OX0QttZL2ovaDsFpLb26J5otfRFRh'
            '&search='
       #     'product_description:"980 ventilator"'
             #'+recall_number:"Z-1208-2018"'
         #    '+report_date:[20190101+TO+20191231]'
             '&sort=recall_initiation_date:desc'
             '&limit=100')
    update_url = url+'&skip='+str(skip)
    response = requests.get(update_url).json()
    data = ENFORCEMENT_DF(response)
    list_of_data.append(data)


combine_df = pd.concat(list_of_data)
combine_df = combine_df.reset_index(drop=True)

###add new col of initiation_year

initiated_yr = []
text_col = combine_df['recall_initiation_date'].tolist()
for i in text_col:
    year = re.search(r'^.{0,4}', i).group(0)
    initiated_yr.append(year)

combine_df['initiated_yr'] = initiated_yr
combine_df.to_csv('total_recall.csv', index=False)
