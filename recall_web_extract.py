 
  
url_19 = "https://www.fda.gov/medical-devices/medical-device-recalls/2019-medical-device-recalls"

url_18 = "https://www.fda.gov/medical-devices/medical-device-recalls/2018-medical-device-recalls"

def scrape_page_find_table():
    url = url_18
    response = requests.get(url).text
    soup = bs4.BeautifulSoup(response, "html.parser") 
    table = soup.find("table")
    title_tag = table.find_all('a')
    date_tag = table.find_all('td')   
    return title_tag, date_tag

title_tag, date_tag = scrape_page_find_table()


######
###graps device name in each link

#create link list of all links
title_lst = []
link_lst = []

for link in title_tag:
    title = link.text
    title_lst.append(title)
    
    short_link = link.attrs['href']
    link_last_portion = short_link.split('/')[-1]
    full_link = urljoin('https://www.fda.gov', short_link)
    link_lst.append(full_link)
    
#create df of link lst

link_df = pd.DataFrame(list(zip(title_lst, link_lst)), columns =['title', 'web_link'])

link_df['date_firm_initiated_recall'] = 'none'

###2019 version
count = 0
for i in range(link_df.shape[0]):
    url = link_df.loc[i, 'web_link']   
    response = requests.get(url).text   
    soup = bs4.BeautifulSoup(response, "html.parser") 
    import re
    tag = soup.find_all(["h2", "h3", "p", "li", "ul", "h4", "strong"], string=re.compile(r"Recalled Product"))
    if tag: 
        for item in tag:
            reason_par = str(item.find_next_sibling())       
            title = re.findall(r'.*:', reason_par)
            import re
            res = re.findall(r'\:(.*)', reason_par)
            for tit, result in zip(title, res):
                if tit == 'Date Initiated by Firm:':
                    link_df.loc[i,'date_firm_initiated_recall'] = result

#2018 version
count = 0
for i in range(link_df.shape[0]):
    url = link_df.loc[i, 'web_link']   
    response = requests.get(url).text   
    soup = bs4.BeautifulSoup(response, "html.parser") 
    import re
    tag = soup.find(["h2", "h3", "p", "li", "ul", "h4", "strong"], string=re.compile(r"Date Recall Initiated"))
    if tag.find_next_sibling():
        link_df.loc[i, 'date_firm_initiated_recall'] = tag.find_next_sibling().text
        
#fix empty rows in date_firm_initiated_recall in 2018

index_exception = list(link_df[link_df['date_firm_initiated_recall'] == ''].index)   

link_df.loc[0, 'date_firm_initiated_recall'] = "October 5, 2018"  
link_df.loc[5, 'date_firm_initiated_recall'] = "September 14, 2018"
link_df.loc[28, 'date_firm_initiated_recall'] = "January 22, 2018"
         
#***********************************

#add date_fda_recall
date_fda_recall = []

for link in date_tag:
    str_link = str(link)
    if not str_link.startswith('<td><a'):
        date = re.search(r'<td>(.*?)</td>', str_link).group(1)      
        date_fda_recall.append(date)
        
link_df['recall_date'] = date_fda_recall     

        
#####*************************************
#extract device, company, reasons   

link_df['brand_name'] = 'none'
link_df['firm_name'] = 'none'
link_df['recall_reason'] = 'none'


###2019 VERSION
for i in range(link_df.shape[0]): 
    title = link_df['title_temp'][i]     
    if not "due to" in title:
        print('EXCEPTION:', i, title, '\n')
    else:         
        device = re.search(r'((?<= Recalls)(.*)(?= Due to))|(?<= Recalls)(.*)(?= for)', title).group(0)
        company = re.search(r'.*(?=Recalls)', title).group(0)
        reason = re.search(r'((?<=Due to).*)|((?<=for).*)', title).group(0)        
        link_df.loc[i, 'brand_name'] = device
        link_df.loc[i, 'firm_name'] = company
        link_df.loc[i, 'recall_reason'] = reason

         
#extract index of missing rows in firm_name, brand_name, reason        
index_exception = list(link_df[link_df['brand_name'] == 'none'].index)        
        
#add companies to missing values in firm_name
company_append = ['Medtronic','Ethicon', 'Becton Dickinson (BD) (CareFusion 303, Inc.)', 
           'Ethicon', 'Draeger Medical']

for i, firm_name in zip(index_exception, company_append):
    link_df.loc[i, 'firm_name'] = firm_name
    
#add devices to missing values in brand_name
device_append = ['Remote Controllers for MiniMed Insulin Pumps', 
                 'ECHELON FLEX ENDOPATH Staplers', 
                'Alaris Pump Module Model 8100 Bezel Assembly',
               'Circular Staplers',
               'Breathing Circuits and Anesthesia Sets']


for i, device in zip(index_exception, device_append):
    link_df.loc[i, 'brand_name'] = device

#add reason to missing values in recall_reason

reason_append = ['Potential Cybersecurity Risks', 
             'Failure to Completely Form Staples', 
         'Free Flow, Over-Infusion, Under-Infusion, or Interruption of Infusion', 
        'Insufficient Firing and Failure to Completely Form Staples', 'None' ]

for i, reason in zip(index_exception, reason_append):
    link_df.loc[i, 'recall_reason'] = reason


###2018 VERSION
    
link_df['title_temp'] = link_df['title'].str.lower()
    
for i in range(link_df.shape[0]): 
    title = link_df['title_temp'][i]     
    if not "recalls" in title:
        print('EXCEPTION:', i, title, '\n')
    else:         
        device = re.search(r'((?<= recalls)(.*)(?= due to))', title).group(0)
        company = re.search(r'.*(?=recalls)', title).group(0)
        reason = re.search(r'((?<=due to).*)', title).group(0)
        link_df.loc[i, 'brand_name'] = device
        link_df.loc[i, 'firm_name'] = company
        link_df.loc[i, 'recall_reason'] = reason

#add companies to missing values in firm_name
company_append = ['none','draeger medical systems, inc.', 'medtronic', 
           'Monteris Medical Group', 'Sterilmed, Inc.']

for i, firm_name in zip(index_exception, company_append):
    link_df.loc[i, 'firm_name'] = firm_name
    
#add devices to missing values in brand_name
device_append = ['arkon anesthesia delivery system', 
            'jaundice meter jm-103 and jaundice meter jm-105', 
    'medtronic heartware hvad system (HVAD system)',
   'Monteris Medical NeuroBlate System and Laser Delivery Probes',
   'Sterilmed Reprocessed Agilis Steerable Introducer Sheath']

for i, device in zip(index_exception, device_append):
    link_df.loc[i, 'brand_name'] = device

#add reason to missing values in recall_reason

reason_append = ['unexpected failed state while in use or idle', 
             'misinterpretation of display messages for out of range values', 
         'unintended intermittent electrical disconnection between the power source and the controller', 
        'unexpected heating of laser delivery probes', 'improper seal of the sheath hub' ]

for i, reason in zip(index_exception, reason_append):
    link_df.loc[i, 'recall_reason'] = reason

            
#convert date format


link_df['recall_date'] = pd.to_datetime(link_df.recall_date).dt.strftime('%Y%m%d')
link_df['date_firm_initiated_recall'] = pd.to_datetime(link_df.date_firm_initiated_recall).dt.strftime('%Y%m%d')

#export for 2018
link_df.to_csv('recall_web_2018.csv', index = False)


#fix exceptions in 2019
link_df['date_firm_initiated_recall'][21] = 'July 1, 2017'
link_df['date_firm_initiated_recall'][28] = 'May 22, 2019'

link_df['date_firm_initiated_recall'] = pd.to_datetime(link_df['date_firm_initiated_recall'].str.replace('none', '19000101')).dt.strftime('%Y%m%d')
link_df['date_firm_initiated_recall'] = link_df['date_firm_initiated_recall'].str.replace('19000101', 'none')

link_df.to_csv('original_recall_2019_withoutdataset.csv')
#link_df has 49 rows


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

for i in range(link_df.shape[0]):
    url = link_df.loc[i, 'web_link']   
    response = requests.get(url).text   
    soup = bs4.BeautifulSoup(response, "html.parser") 
    import re
    tag = soup.find_all(["h2", "h3"], string=re.compile("Reason for Recall"))
      if tag: 
        for item in tag:
            reason_par = str(item.find_next_sibling().text)  