# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 01:50:10 2020

@author: sinha
"""

import pandas as pd
import numpy as np
import os
from io import TextIOWrapper

pd.options.mode.chained_assignment = None 

def calculate_runningAvg(df, prev_len):
    original_df = df
    for i in range(0 + prev_len, prev_len + len(df)-4):
        df.at[i, 'h_score'] = np.mean(df.loc[i:i+4, 'h_score'])
        print (i)
    
    return pd.DataFrame(df)
    
def merge_Segments(seg_df, delay_or_group, prev_len):
    d_segments = seg_df['Segment'].unique()
        
    n_seg = 0
    for seg in d_segments:
        n_seg += 1
        if delay_or_group == 0:
            seg_df.loc[seg_df['Segment'] == seg, 'Delay'] = seg_df['Group'] + '-' + str(n_seg)
        elif delay_or_group == 1:
            seg_df.loc[seg_df['Segment'] == seg, 'Delay'] = seg_df['Delay'] + '-' + str(n_seg)
    
    avg_seg_df = calculate_runningAvg(seg_df, prev_len)
    
    return pd.DataFrame(seg_df), avg_seg_df

def delete_columns(df, cols):
    df = df.drop(cols, axis = 1)
    if 'Group' in df:
        df = df.drop(['Group'], axis = 1)
    if 'Video Type' in df:
        df = df.drop(['Video Type'], axis = 1)

    return pd.DataFrame(df)


def filter_on_delay(csv):
    delays = csv['Delay'].unique()
    print(delays)
    df = pd.DataFrame()  
    prev_len = 0
    for d in delays:
        d_hscores = csv.loc[csv['Delay'] == d]   
        print ('\n',len(d_hscores))
        merged, merged_avg = merge_Segments(d_hscores, 1, prev_len)
        prev_len += len(d_hscores)
        df = df.append(merged)
   
    cols = ['Unnamed: 0','start', 'end', 'Segment']
    
    df = delete_columns(df, cols)
    return df

def filter_on_group(csv):
    delays = csv['Group'].unique()
    df = pd.DataFrame()    
    prev_len = 0
    for d in delays:
        d_hscores = csv.loc[csv['Group'] == d]        
        print ('\n',len(d_hscores))
        merged, merged_avg = merge_Segments(d_hscores, 1, prev_len)
        prev_len += len(d_hscores)
        df = df.append(merged)
    
    cols = ['Unnamed: 0','start', 'end', 'Segment']
    
    df = delete_columns(df, cols)
    return df

def compute_statistics(dfg):
    stats = dfg.groupby('Delay').mean()
    sizes = dfg.groupby('Delay').size().tolist()
    df_std = dfg.groupby('Delay').std()['h_score']
    df_median = dfg.groupby('Delay').median()['h_score']
    
    stats['mean h_score'] = stats['h_score']
    stats['std h_score'] = df_std
    stats['median h_score'] = df_median
    stats['size'] = sizes
    stats = stats.drop(['h_score'], axis = 1)
    
    stats.to_csv('temp.csv')
    return stats


session_path = "../Sessions/"
session_id = "IM175_1"
processed_file_path = session_path + session_id + "/processed_data"
file_suffix = '_video_analysis_filtered.csv'

csv = pd.read_csv(processed_file_path + '/' + session_id + file_suffix)

pid = csv['PId'][0]
eft_ert_type = csv['Type'][0] 

filtered_csv = pd.DataFrame()

if 'Group' not in csv:
    filtered_csv = filter_on_delay(csv)
else:
    filtered_csv = filter_on_group(csv)
stats = compute_statistics(filtered_csv)
print ('Statistics done')
# stats.reset_index(level=0, inplace = True)
# stats.insert(0, 'PId', pid)
# stats.insert(1, 'Type', eft_ert_type)
# stats.set_index('PId')
# output = pd.DataFrame(stats)
# output.set_index('PId')
# print ('writing')
# with open(processed_file_path + '/' + session_id + '_test.txt', 'w+') as f:
#     f.write('Just testing write operations')
# f.close()
# output.to_csv(processed_file_path + '/' + session_id + '_stats.csv')
# print ('Written successfully\n')