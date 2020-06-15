"""
Created on Mon Jun  8 10:12:42 2020

@author: thanhng
"""

import pandas as pd
import numpy as np
import re

import clean_text
from clean_text import *

#find the list of active recall
#extract text into cols, use regex to filter device names


path = '~/recall_stage2_data/total_recall.csv'

data = pd.read_csv(path)

ongoing = data[data['status']=='Ongoing'].reset_index(drop=True)

first_extract = []
for i in range(ongoing.shape[0]):
    text = ongoing['product_description'][i].split(',')[0]
    first_extract.append(text)


#remove parenthesis

ongoing['second_extract'] = first_extract

for i, text in enumerate(first_extract):
    if len(text)>30:
        temp_text = text.split('  ')[0].split(';')[0].split(':')[0]
        ongoing.loc[i, 'second_extract'] = REMOVE_CHAR_IN_PARENTHESIS(temp_text)


ongoing_save = ongoing.filter(['recall_number', 'status',
                               'recall_initiation_date',
                               'product_description', 'second_extract'])

#check size of unique devices
len(set(ongoing_save['second_extract']))

ongoing_save.isna().sum()

#remove empty rows
ongoing_rm = ongoing_save[ongoing_save['second_extract'].notna()].reset_index(drop=True)



#remove numbers
ongoing_rm['third_extract'] = ongoing_rm['second_extract']

ongoing_rm['third_extract'] = REMOVE_NUMBER_USING_REGEX(ongoing_rm, 'second_extract', 'third_extract')

#############


ongoing_rm['recode_device'] = ongoing_rm['third_extract'].str.lower()

ongoing_rm['recode_device']

ongoing_rm['recode_device'] = RECODE_DEVICE(ongoing_rm, 'recode_device', first_dict)

len(set(ongoing_rm['recode_device']))

#remove punctuation
ongoing_rm['rm_punct'] = ongoing_rm['recode_device'].str.lower()

ongoing_rm['rm_punct'] = REMOVE_PUNCT_REGEXPTOKENIZER(ongoing_rm, 'rm_punct')


len(set(ongoing_rm['rm_punct']))


###after recode, check if old device name still exist in text

CHECK_WORD_EXISTENCE_IN_TEXT(ongoing_rm, 'rm_punct', 'accu chek')


###fix text
ongoing_rm['rm_punct'] = RECODE_DEVICE(ongoing_rm, 'rm_punct', second_dict)


len(set(ongoing_rm['rm_punct']))

ongoing_rm_1 = ongoing_rm.drop_duplicates(subset='rm_punct').reset_index(drop=True)

####save data
ongoing_rm_1 = ongoing_rm_1.filter(['recall_number', 'status','recall_initiation_date', 'product_description', 'rm_punct'])

ongoing_rm_1 = ongoing_rm_1.rename(columns = {'rm_punct': 'device_recode'})

ongoing_rm_1.to_csv('recall_ongoing.csv', index=False)
