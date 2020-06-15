#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 13:01:57 2020
@author: thanhng
"""
import pandas as pd
import numpy as np
import re
import spacy
from spacy.lang.en import English
from datetime import datetime

import nltk
from nltk.tokenize import RegexpTokenizer
import time


nlp = spacy.load("en_core_sci_sm")

######clean text

def LEMMATIZER(doc):
    doc = [token.lemma_ for token in doc if token.lemma_ != '-PRON-']
    doc = u' '.join(doc)
    return nlp.make_doc(doc)

def REMOVE_STOPWORDS(doc):
    doc = [token.text for token in doc if token.is_stop != True]
    doc = u' '.join(doc)
    return nlp.make_doc(doc)

def REMOVE_PUNCT(doc):
    doc = [token for token in doc if not token.is_punct]
    doc = ', '.join(str(word) for word in doc if str(word).isalnum())
    return doc

def GET_UNIQUE_WORD(doc):
    return ', '.join(word for word in set(doc.split(' ')))



#tokenize & remove stopword
def TOKENIZE_RM_STOPWORD(word_lst):
    tokenize = nltk.word_tokenize(str(word_lst))

    punct=["[", "]", ",", "'", "none", "...", ":"]
    return[token for token in tokenize if token not in punct]

####remove character in paren
def REMOVE_CHAR_IN_PARENTHESIS(text):
    ''' remove 'abd123' in (abd123)
    must have both parentheses '(' AND ')'
    need to modify if only have 1 ')'
    '''
    while True:
        try:
            if '(' and ')' in text:
                span_index = re.search(r'\([^()]*\)', text).span(0)
                return text[:span_index[0]-1] + ' ' + text[span_index[1]+1:]
            else:
                return text
                break
        except AttributeError:
            print('ERROR', text)
            break

##############
def REMOVE_NUMBER_USING_REGEX(data, col, return_col):
    '''after tokenize words, use regex to remove number such as abc123htj, mf123  '''
    for i, text in enumerate(data[col]):
        data.loc[i, return_col] = re.sub('[0-9]', '', text)
    return data[return_col]



#######recode
def RECODE_DEVICE(data, col, abbr_dict):
    '''use to fix typo, abbreviation, or recode a term, using (key, value) in dictionary '''
    for i, text in enumerate(data[col]):
        for key, val in abbr_dict.items():
            key = key.lower()
            val = val.lower()
            regex_key = r'\b' + key + r'\b'
            result = re.search(regex_key, str(text), flags = re.IGNORECASE)
            if result:
                data.loc[i, col] = val
    return data[col]


######remove punct using regex
def REMOVE_PUNCT_REGEXPTOKENIZER(data, col):
    '''do not need to tokenize words in advance
    use for single word such as 'viva-e', 'hamilton-6s' '''
    for i, text in enumerate(data[col]):
        tokenizer = RegexpTokenizer(r'\w+')
        new_text = ' '.join(word for word in tokenizer.tokenize(text))
        data.loc[i, col] = new_text
    return data[col]


####check if a word exist in text columns
def CHECK_WORD_EXISTENCE_IN_TEXT(data, col, word):
    for i, text in enumerate(data[col]):
        result = re.search(r'\b' + word + r'\b', text, flags = re.IGNORECASE)
        if result:
            print(i, text, '\n')

#unigram
def UNIGRAM(word_lst, N):
    tokenize_lst = TOKENIZE_RM_STOPWORD(word_lst)
    unigram = nltk.FreqDist(tokenize_lst).most_common(N)
    return pd.DataFrame(unigram,columns=['Unigram', 'Unigram_Frequency'])

#bigrams
def BIGRAM(word_lst, N):
    tokenize_lst = TOKENIZE_RM_STOPWORD(word_lst)
    bigram = nltk.FreqDist(list(nltk.bigrams(tokenize_lst))).most_common(N)
    return pd.DataFrame(bigram,columns=['Bigram', 'Bigram_Frequency'])

#trigrams
def TRIGRAM(word_lst, N):
    tokenize_lst = TOKENIZE_RM_STOPWORD(word_lst)
    trigram = nltk.FreqDist(list(nltk.trigrams(tokenize_lst))).most_common(N)
    return pd.DataFrame(trigram,columns=['Trigram', 'Trigram_Frequency'])

def NGRAM(text_column):
    uni = UNIGRAM(text_column, 50)
    bigram = BIGRAM(text_column, 50)
    trigram = TRIGRAM(text_column, 50)
    return pd.concat([uni, bigram, trigram], axis = 1)


def EXTRACT_DATA(col, value):
    return data[data[col] == value].reset_index(drop=True)
