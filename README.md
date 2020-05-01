to-be-continue...

## Exploratory analysis on MAUDE and recall dataset

#### Topic: medical devices
#### Method: data wrangling
#### Tools: python + tableau
#### Data source: 
  - FDA adverse event for medical devices: https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfmaude/search.cfm
  - FDA medical device recall: https://www.fda.gov/medical-devices/medical-device-recalls/2019-medical-device-recalls


__Background__: MAUDE is the FDA public dataset to track medical device adverse events. Anyone can submit reports to the FDA 
including both healthcare and non-healthcare professionals (such as nurses, pharmacists, biomedical engineers, lawyers, patients, 
etc.). Doesn't matter the incident directly or indirectly involve in the suspect medical device, people are encouraged to report to the FDA. 

Medical device recall dataset is another public FDA website regarding information about recall. 


#### Project objective: What kind of report in MAUDE that can lead to a recall? 

- Once a report appeard in MAUDE, how long does it take FDA to take action? 
  - How long does it take from the _first adverse event_ to the recall date? Does it need to be adverse event to catch their attention? 
  - How long does it take from the _first malfunction/injury/death_ event to the recall date?
  - If there is a big year gap, why there is a delay? What are the underlying reasons?
- What kind of devices that have the shortest life cycle? 

__Limitations__:
- MAUDE is a big dataset with more than 6 million rows from 1990 until 2020. Searching for a device in MAUDE is complicated
because the device names being reported are not consistent.
- Recall dataset is another messy data since 1 device can be recalled many times within 1 year for many different reasons.Thus, 
it is difficult to keep track of what is the earliest recall date on the website. Here I only looked at recalls in 2018 and 2019. 
  
