to-be-continue...

__Project title__: Exploratory analysis on MAUDE and recall databases

__Project objective__: what kind of reports in MAUDE that can lead to a recall? 

__Background__: MAUDE is the FDA public database to track medical device adverse events. Anyone can submit reports to the FDA 
including both healthcare and non-healthcare professionals (such as nurses, pharmacists, biomed engineers, lawyers, patients, 
etc.). Doesn't matter the incident directly or indirectly involve in the suspect medical device, people are encourage to report to the FDA. 

Medical device recall database is another public FDA website regarding information about recall. Thus, the objective of this project
is to find the relationship between these two database. In specific:

- Once a report about a specific device appeard on MAUDE, how long does it take FDA to take action? 
  - how long does it take from the first adverse event to the recall date? 
  - how long does it take from the first malfunction/injury/death event to the recall date?
  - if there is a big year gap, why there is a delay? what are the underlying reasons?
- what kind of devices that have the shortest life cycle? 

__Limitations__:
- MAUDE is a big dataset with more than 6 million rows from 1990 until 2020. Searching for a device in MAUDE is complicated
because the device names being reported are not consistent.
- Recall database is another messy data since 1 device can be recalled many times within 1 year for many different reasons.Thus, 
it is difficult to keep track of what is the earliest recall date on the website. Here I only looked at recalls in 2018 and 2019. 
  
