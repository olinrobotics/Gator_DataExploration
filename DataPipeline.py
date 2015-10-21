import pandas as pd
import datetime as dt
from ScanClassDef import *
import math

def ProcessData(filepath):
    
    """
    This function takes the filepath to a csv containing scan data and processes it to produce
    a dataset as a dictionary for subsequent work.

    filepath: String representing the filepath to the csv of data

    Returns cleaned_dataset, which is a dictionary containing the scan objects for each scan 
    in the recorded data.
    """

    #Sets up the header list which is just a row of column indices from 1 to 100
    header_list=range(0, 100) 

    #Read the CSV into a pandas dataframe
    dataset=pd.read_csv(filepath, sep=',', names=header_list) 

    #Gets the total number of rows in the data frame
    rowcount=dataset.shape[0]

    #Because we recorded data in stacks of 100 in the csv, I need to know how many stacks I need to retrieve; Divided by 186
    #because there are 185 data points (6 data points for vehicle pose, time etc. and 179 lidar points)
    num_sets=rowcount/186

    #Sets the start and end index so that we can split the huge pandas dataframe into the individual stacks
    start_index=[0]
    end_index=[185]

    #Sets up a dictionary to hold the pandas dataframes for each stack of data
    pd_dict={}

    # print num_sets

    for i in range(num_sets):
        if i==0:
            
            #If we're looking at the first stack of data, we already placed its start and end index into the row so all we 
            #need to do is actually retrieve the slice of the original dataframe.
            pd_dict[i]=dataset[start_index[i]:end_index[i]]
        
        else:
            
            #If it's not the first stack, then we need to add the appropriate start and end index to the list so that we
            #know where to start and end index to get subsequent stacks of data
            starting=start_index[-1]+186
            start_index.append(starting)
            
            ending=end_index[-1]+186
            end_index.append(ending)
            
            raw_dataframe=dataset[start_index[i]:end_index[i]]
            raw_dataframe_cols=raw_dataframe.columns
            
            if raw_dataframe.isnull().any().any():
                
                test_row=raw_dataframe.iloc[0,:]
                
                end=0
                working_cols=[]
                for j in range(len(test_row)):
    #                 print test_row[j]
                    if math.isnan(float(test_row[j])):
    #                     print "Hi"
    #                     print math.isnan(test_row[j])
                        end=j
                        break
                    else:
                        working_cols.append(raw_dataframe[raw_dataframe_cols[j]])

                raw_dataframe_clean=pd.concat(working_cols, axis=1)
                
    #             print raw_dataframe_clean
                
                #Retrieves the appropriate slice from the dataframe
                pd_dict[i]=raw_dataframe_clean
            
                #Resets the index so that the concatenate function later on doesn't do weird stuff with column-wise concatenation
                pd_dict[i] = pd_dict[i].reset_index(drop=True)
                        
            else:
                #Retrieves the appropriate slice from the dataframe
                pd_dict[i]=dataset[start_index[i]:end_index[i]]
            
                #Resets the index so that the concatenate function later on doesn't do weird stuff with column-wise concatenation
                pd_dict[i] = pd_dict[i].reset_index(drop=True)
        key_list=pd_dict.keys()

        #Creates that list of dataframes for use later
        df_list=[]

    #Iterates through the list of keys and for each key,retrieves the dataframe and appends it into the list
    for key in key_list:
        df_list.append(pd_dict[key])

    #Concatenates the individual stacks of dataframes so that all time points are columns in the dataframe rather than the 
    #weird stacking that was present in the original dataset
    final_df=pd.concat(df_list, axis=1)

    #Shows the dataframe to confirm concatenation was carried out as expected
    final_df

    #Creates list of new column names to rename columns from 0 - 100 repeating to become 0 - 400
    new_ColumnName=range(0,len(final_df.columns))

    #Assigns the new column names to the dataframe; Dataframe is now sufficiently clean
    final_df.columns=new_ColumnName

    #Creates the final data dictionary that will be used to store all recorded scans
    cleaned_dataset={}

    #Iterates through each column in the full dataframe and creates a scan object for each one
    for col in final_df.columns:

        #Gets the column as a pandas series
        column=final_df[col]

        #Creates the Scan object using the pandas series
        scan_obj=Scan(column)

        #Adds the Scan object to the data dictionary using the column number as the key
        cleaned_dataset[col]=scan_obj

    #Returns the final data dictionary
    return cleaned_dataset