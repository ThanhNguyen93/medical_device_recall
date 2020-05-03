def COMBINED_CSV():
	'''combine all csv files within a folder'''
	extension = 'csv'
	all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
	print('check file names: ', all_filenames)

	#combine all data
	combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ]).reset_index(drop=True)
	return combined_csv

def READ_DATA(filename):
	'''filename should be in str(.csv) '''
	data = pd.read_csv(filename)
	print('SHAPE: ', data.shape)
	print(data.head)
	return data



#sort datasets alphabetically
def SORT_DATA_ALPHABET(data):
	combined_data = data.sort_values('dataset')
	return combined_csv


def GROUP_BY_DATASET(sorted_data, tracking_df):
	group_dataset = sorted_data.groupby('dataset')
	group_tracking = tracking_df.groupby('dataset')
	return group_dataset, group_tracking



#sort data by dates
''' need fix!
def SORT_BY_DATE(data, dataset_name):
    group_dataset = data.groupby('dataset')
    df_index = data.loc[group_dataset.groups.get(dataset_name)].index
    data.loc[df_index, ].sort_values(by=['date_of_event_edit'], na_position='last')
    print(data)
    return sorted_data
	'''

#count number of reports

def CREATE_TRACKING_DF(data):
	tracking_df = data['dataset'].value_counts().rename_axis('dataset').reset_index(name='counts_in_maude').sort_values('dataset')
	tracking_df = tracking_df.reset_index(drop=True)
	return tracking_df


def COUNT_MISSING(data, tracking_df):
	group_dataset = data.groupby('dataset')
	group_tracking = tracking_df.groupby('dataset')
	for name in dataset_name:
	   result = data.loc[group_dataset.groups.get(name)].isna().sum()
	   tracking_df.loc[group_tracking.groups.get(name), 'missing_in_AE'] = result.values[4]
	   tracking_df.loc[group_tracking.groups.get(name), 'missing_event_date'] = result.values[5]
	return tracking_df


def COUNT_EVENT_TYPE(data, tracking_df):
	group_dataset = data.groupby('dataset')
	group_tracking = tracking_df.groupby('dataset')
	for name in dataset_name:
	    count = data.loc[group_dataset.groups.get(name)]['event_type'].value_counts()
	    for i, j in zip(count.index, count.values):
	        if i == 'Malfunction':
	            tracking_df.loc[group_tracking.groups.get(name), '#_of_malfunction'] = j
	        if i == 'Injury':
	            tracking_df.loc[group_tracking.groups.get(name), '#_of_injury'] = j
	        if i == 'Death':
	            tracking_df.loc[group_tracking.groups.get(name), '#_of_death'] = j
	return tracking_df


def COUNT_AE(data, tracking_df):
    group_dataset = data.groupby('dataset')
    for name in dataset_name:
	    count = data.loc[group_dataset.groups.get(name)]['adverse_event_flag'].value_counts()
	    for i, j in zip(count.index, count.values):
	        if i == 'Y':
	            tracking_df.loc[group_tracking.groups.get(name), '#_of_AE'] = j
    return tracking_df


def GET_FIRST_EVENT_TYPE(data, tracking_df):
    group_dataset = data.groupby('dataset')
    group_tracking = tracking_df.groupby('dataset')
    dataset_name = tracking_df['dataset']

    for name in dataset_name:
	    res = sorted_data.loc[group_dataset.groups.get(name)].groupby('event_type').first()['date_of_event']
	    for i, j in zip(res.index, res.values):
	         if i == 'Malfunction':
	            tracking_df.loc[group_tracking.groups.get(name), 'first_malfunction'] = j
	         if i == 'Injury':
	            tracking_df.loc[group_tracking.groups.get(name), 'first_injury'] = j
	         if i == 'Death':
	            tracking_df.loc[group_tracking.groups.get(name), 'first_death'] = j
    return tracking_df



def GET_FIRST_DATE(data, tracking_df):
	'''get first date_of_event in MAUDE '''
	first_date = pd.DataFrame(data.groupby('dataset').first()['date_of_event']).reset_index()
	first_date.columns = ['dataset', 'maude_first_date']
	tracking_df = pd.merge(tracking_df, first_date, on = 'dataset')
	return tracking_df
