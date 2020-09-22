
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 04:32:02 2020

@author: sinha
"""

import pandas as pd
import os
from io import TextIOWrapper

# pd.options.mode.chained_assignment = None 

def merge_Segments(seg_df, delay_or_group):
    d_segments = seg_df['Segment'].unique()
    n_seg = 0
    for seg in d_segments:
        n_seg += 1
        if delay_or_group == 0:
            seg_df.loc[seg_df['Segment'] == seg, 'Delay'] = seg_df['Group'] + '-' + str(n_seg)
            # seg_df['Delay'][seg_df['Segment'] == seg] = seg_df['Group'] + '-' + str(n_seg)
            # seg_df['Parts'][seg_df['Segment'] == seg] = n_seg
        elif delay_or_group == 1:
            seg_df.loc[seg_df['Segment'] == seg, 'Delay'] = seg_df['Delay'] + '-' + str(n_seg)
            # seg_df['Delay'][seg_df['Segment'] == seg] = seg_df['Delay'] + '-' + str(n_seg)
            # seg_df['Parts'][seg_df['Segment'] == seg] = n_seg
    return pd.DataFrame(seg_df)

def delete_columns(df, cols):
    df = df.drop(cols, axis = 1)
    if 'Group' in df:
        df = df.drop(['Group'], axis = 1)
    if 'Video Type' in df:
        df = df.drop(['Video Type'], axis = 1)
    
    return pd.DataFrame(df)

def filter_on_delay(csv):
    delays = csv['Delay'].unique()
    df = pd.DataFrame()    
    for d in delays:
        d_hscores = csv.loc[csv['Delay'] == d]        
        merged = merge_Segments(d_hscores, 1)
        df = df.append(merged)
   
    # print (df)
    # updated_delay = df.pop('Delay')
    cols = ['Unnamed: 0','start', 'end', 'Segment']
    
    df = delete_columns(df, cols)
    # df.insert(2, 'Delay', updated_delay)
    return df

def filter_on_group(csv):
    delays = csv['Group'].unique()
    df = pd.DataFrame()    
    for d in delays:
        d_hscores = csv.loc[csv['Group'] == d]        
        d_hscores = merge_Segments(d_hscores, 0)
        df = df.append(d_hscores)
    
    # updated_delay = df.pop('Delay')
    cols = ['Unnamed: 0','start', 'end', 'Segment']
    
    df = delete_columns(df, cols)
    # df.insert(2, 'Delay', updated_delay)
    return df

def compute_statistics(dfg):
    stats = dfg.groupby('Delay').mean()
    df_std = dfg.groupby('Delay').std()['h_score']
    df_median = dfg.groupby('Delay').median()['h_score']
    
    stats['mean h_score'] = stats['h_score']
    stats['std h_score'] = df_std
    stats['median h_score'] = df_median
    stats = stats.drop(['h_score'], axis = 1)
    
    stats.to_csv('temp.csv')
    return stats
    

session_path = "../Sessions/"
session_id = "IM175_1"

def main():
    home_path = os.getcwd()
    print (home_path)
    session_names = os.listdir(session_path)
    for session_id in session_names:
        try:
            print ('\n\n------------- Processing files of ' + session_id + ' for statistics -----------')
            processed_file_path = session_path + session_id + "/processed_data/"
            file_suffix = '_video_analysis_filtered.csv'
            
            csv = pd.read_csv(processed_file_path + session_id + file_suffix)
            print('read csv')
            pid = csv['PId'][0]
            eft_ert_type = csv['Type'][0] 
            
            filtered_csv = pd.DataFrame()
            
            if 'Group' not in csv:
                filtered_csv = filter_on_delay(csv)
                print('Filtered perfectly')
            else:
                filtered_csv = filter_on_group(csv)
                print('Filtered perfectly')
            stats = compute_statistics(filtered_csv)
            print ('Statistics done')
            stats.reset_index(level=0, inplace = True)
            print('reset done')
            stats.insert(0, 'PId', pid)
            stats.insert(1, 'Type', eft_ert_type)
            print('insert done')
            print('Reached before writing')
            stats.set_index('PId')
            output = pd.DataFrame(stats)
            output.set_index('PId')
            print (output)
            # os.chdir(processed_file_path)
            # print(os.getcwd())
            output_file = session_id + '_stats.csv'
            print ('writing')
            # print (output_file)
            # with open(processed_file_path + output_file, mode='w', newline='\n') as f:
            #     stats.to_csv(f, sep=self.delimiter, index=False)
            output.to_csv(processed_file_path + session_id + '_stats.csv')
            print ('Written successfully\n')
            # os.chdir(home_path)
        except:
            pass
            

if __name__ == "__main__":
    main()