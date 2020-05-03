from bs4 import BeautifulSoup
import os, requests
import pandas as pd
from urllib.parse import urljoin, urlparse
import re

url_19 = "https://www.fda.gov/medical-devices/medical-device-recalls/2019-medical-device-recalls"
url_18 = "https://www.fda.gov/medical-devices/medical-device-recalls/2018-medical-device-recalls"

def SCAPE_WEBPAGE(url):
    response = requests.get(url).text
    soup = BeautifulSoup(response, "html.parser")
    table = soup.find("table")
    title_tag = table.find_all('a')
    date_tag = table.find_all('td')
    return title_tag, date_tag

title_tag, date_tag = SCAPE_WEBPAGE(url_19)

######

''' download all the html files and store them in a folder (in case the website 
change but your code will not break because of that)'''

def SAVE_HTML(link, data_dir):    
        short_link = link.attrs['href']
        add_html = "{}.html".format(short_link.split('/')[-1])
        full_link = urljoin('https://www.fda.gov', short_link)
        get_detail_page = requests.get(full_link).content
    
        outfile = os.path.join(data_dir, add_html)
        with open(outfile, mode = 'wb') as file:
            file.write(get_detail_page)

data_dir = '/Users/thanhng/medical_device_recall/html_pages_2019'

for link in title_tag:
    SAVE_HTML(link, data_dir)
    

#create web tracking df
web_tracking = []
for link in title_tag:
    title = link.text
    full_link = urljoin('https://www.fda.gov', link.attrs['href'])    
    web_tracking.append({'title': title, 
                        'web_link': full_link
                               })
    
web_tracking_df = pd.DataFrame(web_tracking)

def GET_PAGE_CONTENT(url):
    response = requests.get(url).text
    page_content = BeautifulSoup(response, "html.parser")
    return page_content

'''Get date_firm_initiated_recall '''

web_tracking_df['date_firm_initiated_recall'] = 'none'

###2019 version

for i in range(web_tracking_df.shape[0]):
    url = web_tracking_df.loc[i, 'web_link']
    page_content = GET_PAGE_CONTENT(url)
    import re
    tag = page_content.find_all(["h2", "h3", "p", "li", "ul", "h4", "strong"], \
                                    string=re.compile(r"Recalled Product"))
    if tag:
        for item in tag:
            sibling = str(item.find_next_sibling())
            title = re.findall(r'.*:', sibling)
            import re
            content = re.findall(r'\:(.*)', sibling)
            import re
            for each_title, each_content in zip(title, content):
                if each_title == 'Date Initiated by Firm:':
                    web_tracking_df.loc[i,'date_firm_initiated_recall']  = each_content

#2018 version
for index in range(web_tracking_df.shape[0]):
    url = web_tracking_df.loc[index, 'web_link']
    page_content = GET_PAGE_CONTENT(url)
    import re
    tag = page_content.find(["h2", "h3", "p", "li", "ul", "h4", "strong"],
                            string=re.compile(r"Date Recall Initiated"))
    if tag.find_next_sibling():
        web_tracking_df.loc[index, 'date_firm_initiated_recall'] = \
                                            tag.find_next_sibling().text

#fix empty rows in date_firm_initiated_recall in 2018

index_exception = list(web_tracking_df[web_tracking_df['date_firm_initiated_recall'] == ''].index)

web_tracking_df.loc[0, 'date_firm_initiated_recall'] = "October 5, 2018"
web_tracking_df.loc[5, 'date_firm_initiated_recall'] = "September 14, 2018"
web_tracking_df.loc[28, 'date_firm_initiated_recall'] = "January 22, 2018"

#***********************************

''' add date_fda_recall'''
date_fda_recall = []

for link in date_tag:
    str_link = str(link)
    if not str_link.startswith('<td><a'):
        date = re.search(r'<td>(.*?)</td>', str_link).group(1)
        date_fda_recall.append(date)

web_tracking_df['recall_date'] = date_fda_recall


#####*************************************
'''extract device, company, reasons'''

web_tracking_df['brand_name'] = 'none'
web_tracking_df['firm_name'] = 'none'
web_tracking_df['recall_reason'] = 'none'

def CHECK_TITLE_EXCEPTION(title, year):
        if year == '2019': 
            if not "due to" in title:
                print('EXCEPTION:', i, title, '\n')
                return True
        if year == '2018':
            if not "recalls" in title:
                print('EXCEPTION:', i, title, '\n')
                return True
        return False
   
                  
def EXTRACT_INFO_TITLE(title, year):
    import re
    if CHECK_TITLE_EXCEPTION(title, year):
        device = company =  reason = 'none'
        return device, company, reason
    
    if CHECK_TITLE_EXCEPTION(title, year) == False:
        if year == '2019':
            device = re.search(r'((?<= Recalls)(.*)(?= Due to))|(?<= Recalls)(.*)(?= for)', title, re.IGNORECASE).group(0)
        if year == '2018':
            device = re.search(r'((?<= recalls)(.*)(?= due to))', title, re.IGNORECASE).group(0)
        company = re.search(r'.*(?=Recalls)', title, re.IGNORECASE).group(0)
        reason = re.search(r'((?<=Due to).*)|((?<=for).*)', title, re.IGNORECASE).group(0)
        return device, company, reason 

###2019 VERSION

web_tracking_df'title'] = web_tracking_df['title'].str.lower()
        

for i in range(web_tracking_df.shape[0]):
    title = web_tracking_df['title'][i]
    device, company, reason = EXTRACT_INFO_TITLE(title, '2019')   
    web_tracking_df.loc[i, 'brand_name'] = device
    web_tracking_df.loc[i, 'firm_name'] = company
    web_tracking_df.loc[i, 'recall_reason'] = reason


#extract index of missing rows in firm_name, brand_name, reason
index_exception = list(web_tracking_df[web_tracking_df['brand_name'] == 'none'].index)

#add companies to missing values in firm_name
company_append = ['Medtronic','Ethicon', 'Becton Dickinson (BD) (CareFusion 303, Inc.)',
           'Ethicon', 'Draeger Medical']

for i, firm_name in zip(index_exception, company_append):
    web_tracking_df.loc[i, 'firm_name'] = firm_name

#add devices to missing values in brand_name
device_append = ['Remote Controllers for MiniMed Insulin Pumps',
                 'ECHELON FLEX ENDOPATH Staplers',
                'Alaris Pump Module Model 8100 Bezel Assembly',
               'Circular Staplers',
               'Breathing Circuits and Anesthesia Sets']


for i, device in zip(index_exception, device_append):
    web_tracking_df.loc[i, 'brand_name'] = device

#add reason to missing values in recall_reason

reason_append = ['Potential Cybersecurity Risks',
             'Failure to Completely Form Staples',
         'Free Flow, Over-Infusion, Under-Infusion, or Interruption of Infusion',
        'Insufficient Firing and Failure to Completely Form Staples', 'None' ]

for i, reason in zip(index_exception, reason_append):
    web_tracking_df.loc[i, 'recall_reason'] = reason


###2018 VERSION

for i in range(web_tracking_df.shape[0]):
    title = web_tracking_df['title'][i]
    device, company, reason = EXTRACT_INFO_TITLE(title, '2018')
    web_tracking_df.loc[i, 'brand_name'] = device
    web_tracking_df.loc[i, 'firm_name'] = company
    web_tracking_df.loc[i, 'recall_reason'] = reason

#add companies to missing values in firm_name
company_append = ['none','draeger medical systems, inc.', 'medtronic',
           'Monteris Medical Group', 'Sterilmed, Inc.']

for i, firm_name in zip(index_exception, company_append):
    web_tracking_df.loc[i, 'firm_name'] = firm_name

#add devices to missing values in brand_name
device_append = ['arkon anesthesia delivery system',
            'jaundice meter jm-103 and jaundice meter jm-105',
    'medtronic heartware hvad system (HVAD system)',
   'Monteris Medical NeuroBlate System and Laser Delivery Probes',
   'Sterilmed Reprocessed Agilis Steerable Introducer Sheath']

for i, device in zip(index_exception, device_append):
    web_tracking_df.loc[i, 'brand_name'] = device

#add reason to missing values in recall_reason

reason_append = ['unexpected failed state while in use or idle',
             'misinterpretation of display messages for out of range values',
         'unintended intermittent electrical disconnection between the power source and the controller',
        'unexpected heating of laser delivery probes', 'improper seal of the sheath hub' ]

for i, reason in zip(index_exception, reason_append):
    web_tracking_df.loc[i, 'recall_reason'] = reason


#convert date format


web_tracking_df['recall_date'] = pd.to_datetime(web_tracking_df.recall_date).dt.strftime('%Y%m%d')
web_tracking_df['date_firm_initiated_recall'] = pd.to_datetime(web_tracking_df.date_firm_initiated_recall).dt.strftime('%Y%m%d')

#export for 2018
web_tracking_df.to_csv('recall_web_2018.csv', index = False)


#fix exceptions in 2019
web_tracking_df['date_firm_initiated_recall'][21] = 'July 1, 2017'
web_tracking_df['date_firm_initiated_recall'][28] = 'May 22, 2019'

web_tracking_df['date_firm_initiated_recall'] = pd.to_datetime(web_tracking_df['date_firm_initiated_recall'].str.replace('none', '19000101')).dt.strftime('%Y%m%d')
web_tracking_df['date_firm_initiated_recall'] = web_tracking_df['date_firm_initiated_recall'].str.replace('19000101', 'none')

web_tracking_df.to_csv('original_recall_2019_withoutdataset.csv')
#web_tracking_df has 49 rows


#****************************************************************************


###merge recall19 in WEBSITE with tracking in MAUDE tracking_new.csv' (MAUDE_TRACKING has 57 rows, 16cols)
#result is df 'complete recall 19' (website + tracking)

tracking = pd.read_csv('tracking_new.csv')
original = pd.read_csv('original_recall_2019_dataset.csv')

#return 43 rows, 23 cols
recall_2019_complete = pd.merge(original, tracking, on='dataset')

recall_2019_complete.to_csv('complete_recall_2019.csv', index = False)


###merege recall19 to the rest of tracking (include devices not in recall19), expect 57 cols

merge_df = pd.merge(recall_2019_complete, tracking,on = 'dataset', how = 'right')
merge_df.to_csv('recall_complete.csv', index = False)



####extract reason for recall PARAGRAPH in WEBSITE

for i in range(web_tracking_df.shape[0]):
    url = web_tracking_df.loc[i, 'web_link']
    response = requests.get(url).text
    soup = bs4.BeautifulSoup(response, "html.parser")
    import re
    tag = soup.find_all(["h2", "h3"], string=re.compile("Reason for Recall"))
      if tag:
        for item in tag:
            reason_par = str(item.find_next_sibling().text)
