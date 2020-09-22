
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 04:32:02 2020

@author: sinha
"""

import pandas as pd
import os
from io import TextIOWrapper
import numpy as np

pd.options.mode.chained_assignment = None 

# def merge_Segments(seg_df, delay_or_group):
#     d_segments = seg_df['Segment'].unique()
#     n_seg = 0
#     for seg in d_segments:
#         n_seg += 1
#         if delay_or_group == 0:
#             seg_df.loc[seg_df['Segment'] == seg, 'Delay'] = seg_df['Group'] + '-' + str(n_seg)
#         elif delay_or_group == 1:
#             seg_df.loc[seg_df['Segment'] == seg, 'Delay'] = seg_df['Delay'] + '-' + str(n_seg)
#     return pd.DataFrame(seg_df)

# def delete_columns(df, cols):
#     df = df.drop(cols, axis = 1)
#     if 'Group' in df:
#         df = df.drop(['Group'], axis = 1)
#     if 'Video Type' in df:
#         df = df.drop(['Video Type'], axis = 1)
    
#     return pd.DataFrame(df)

# def filter_on_delay(csv):
#     delays = csv['Delay'].unique()
#     df = pd.DataFrame()    
#     for d in delays:
#         d_hscores = csv.loc[csv['Delay'] == d]        
#         merged = merge_Segments(d_hscores, 1)
#         df = df.append(merged)
   
#     cols = ['Unnamed: 0','start', 'end', 'Segment']
    
#     df = delete_columns(df, cols)
#     return df

# def filter_on_group(csv):
#     delays = csv['Group'].unique()
#     df = pd.DataFrame()    
#     for d in delays:
#         d_hscores = csv.loc[csv['Group'] == d]        
#         d_hscores = merge_Segments(d_hscores, 0)
#         df = df.append(d_hscores)
    
#     cols = ['Unnamed: 0','start', 'end', 'Segment']
    
#     df = delete_columns(df, cols)
#     return df

# def compute_statistics(dfg):
#     stats = dfg.groupby('Delay').mean()
#     df_std = dfg.groupby('Delay').std()['h_score']
#     df_median = dfg.groupby('Delay').median()['h_score']
    
#     stats['mean h_score'] = stats['h_score']
#     stats['std h_score'] = df_std
#     stats['median h_score'] = df_median
#     stats = stats.drop(['h_score'], axis = 1)
    
#     stats.to_csv('temp.csv')
#     return stats
    

def calculate_runningAvg(df, prev_len):
    original_df = df
    for i in range(0 + prev_len, prev_len + len(df)-4):
        df.at[i, 'h_score'] = np.mean(df.loc[i:i+4, 'h_score'])
    
    return pd.DataFrame(df)
    
# def merge_Segments(seg_df, delay_or_group, prev_len):
#     d_segments = seg_df['Segment'].unique()
        
#     n_seg = 0
#     for seg in d_segments:
#         n_seg += 1
#         if delay_or_group == 0:
#             seg_df.loc[seg_df['Segment'] == seg, 'Delay'] = seg_df['Group'] + '-' + str(n_seg)
#         elif delay_or_group == 1:
#             seg_df.loc[seg_df['Segment'] == seg, 'Delay'] = seg_df['Delay'] + '-' + str(n_seg)
    
#     avg_seg_df = calculate_runningAvg(seg_df, prev_len)
    
#     return pd.DataFrame(seg_df), avg_seg_df

def merge_Segments(seg_df, prev_len):
    d_segments = seg_df['Segment'].unique()
    seg_df['Delay'] = seg_df['Delay'].apply(lambda x: x.split('-')[0])    
    # print (seg_df)
    n_seg = 0
    for seg in d_segments:
        n_seg += 1
        seg_df.loc[seg_df['Segment'] == seg, 'Delay'] = seg_df['Delay'] + '-' + str(n_seg)
    
    # print (seg_df)
    avg_seg_df = calculate_runningAvg(seg_df, prev_len)
    
    return pd.DataFrame(seg_df), avg_seg_df

def delete_columns(df):
    cols = ['Unnamed: 0','start', 'end', 'Segment']
    df = df.drop(cols, axis = 1)
    if 'Group' in df:
        df = df.drop(['Group'], axis = 1)
    if 'Video Type' in df:
        df = df.drop(['Video Type'], axis = 1)

    return pd.DataFrame(df)


def filter_delays(csv):
    csv['Delay'] = csv['Delay'].apply(lambda x: x + '-c')
    original = csv
    delays = csv['Delay'].unique()
    print (delays)
    df = pd.DataFrame()
    df_avg = pd.DataFrame()
    prev_len = 0
    for d in delays:
        d_hscores = csv.loc[csv['Delay'] == d]
        # print (d_hscores)
        # print (d_hscores)
        # print ('\n',len(d_hscores))
        merged, merged_avg = merge_Segments(d_hscores, prev_len)
        prev_len += len(d_hscores)
        
        df = df.append(original.loc[original['Delay'] == d])
        # print (df)
        df = df.append(merged)
        df_avg = df_avg.append(merged_avg)
    # cols = ['Unnamed: 0','start', 'end', 'Segment']
    # print (df)
    df = delete_columns(df)
    df_avg = delete_columns(df_avg)
    # print (df, '\n\n')
    return df, df_avg

# def filter_on_group(csv):
#     delays = csv['Group'].unique()
#     df = pd.DataFrame()  
#     df_avg = pd.DataFrame()
#     prev_len = 0
#     for d in delays:
#         d_hscores = csv.loc[csv['Group'] == d]        
#         # print ('\n',len(d_hscores))
#         merged, merged_avg = merge_Segments(d_hscores, 1, prev_len)
#         prev_len += len(d_hscores)
        
#         # d_hscores['Delay'] = d_hscores['Delay'].apply(lambda x: x['Group'] + '-c')
#         # df = df.append(d_hscores)
#         df = df.append(merged)
#         df_avg = df_avg.append(merged_avg)
#     # cols = ['Unnamed: 0','start', 'end', 'Segment']
    
#     df = delete_columns(df)
#     df_avg = delete_columns(df_avg)
#     return df, df_avg

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
    
    # stats.to_csv('temp.csv')
    return stats

def compute_combined_statistics(csv, pid, eft_ert_type):
    if 'Group' in csv:
        csv['Delay'] = csv['Delay'].apply(lambda x: x['Group'] + '-c')
    else:
        csv['Delay'] = csv['Delay'].apply(lambda x: x + '-c')
    df = delete_columns(csv)
    stats_df = stats_helper(df, pid, eft_ert_type)
    return stats_df
    
def stats_helper(csv, pid, eft_ert_type):
    stats = compute_statistics(csv)
    print ('Statistics done')
    stats.reset_index(level=0, inplace = True)
    stats.insert(0, 'PId', pid)
    stats.insert(1, 'Type', eft_ert_type)
    stats.set_index('PId')
    
    output = pd.DataFrame(stats)
    output.set_index('PId')
    
    return output

session_path = "../Sessions/"
session_id = "IM177_3"
# def main():
#     home_path = os.getcwd()
#     session_names = os.listdir(session_path)
#     for session_id in session_names:
try:
    print ('\n\n------------- Processing files of ' + session_id + ' for statistics -----------')
    processed_file_path = session_path + session_id + "/processed_data"
    file_suffix = '_video_analysis_filtered.csv'
    
    csv = pd.read_csv(processed_file_path + '/' + session_id + file_suffix)
    pid = csv['PId'][0]
    eft_ert_type = csv['Type'][0] 
    
    filtered_csv = pd.DataFrame()
    filtered_avg_csv = pd.DataFrame()
    
    if 'Group' in csv:
        csv['Delay'] = csv['Group']
    
    filtered_csv, filtered_avg_csv = filter_delays(csv)
    # stats = compute_statistics(filtered_csv)
    # stats_avg = compute_statistics(filtered_avg_csv)
    # print ('Statistics done')
    # stats.reset_index(level=0, inplace = True)
    # stats.insert(0, 'PId', pid)
    # stats.insert(1, 'Type', eft_ert_type)
    # stats.set_index('PId')
    # output = pd.DataFrame(stats)
    # output.set_index('PId')
    # original_stats_df = compute_combined_statistics(csv, pid, eft_ert_type)
    output = stats_helper(filtered_csv, pid, eft_ert_type)
    # output = output.append(original_stats_df).sort_values(by = 'Delay')
    
    output_avg = stats_helper(filtered_avg_csv, pid, eft_ert_type)
    # output_avg = output_avg.append(original_stats_df)
    print ('writing')
    # with open(processed_file_path + '/' + session_id + '_test.txt', 'w+') as f:
    #     f.write('Just testing write operations')
    # f.close()
    output.to_csv(processed_file_path + '/' + session_id + '_stats.csv')
    output_avg.to_csv(processed_file_path + '/' + session_id + '_AvgStats.csv')
    print ('Written successfully\n')
    # os.chdir(home_path)
except:
    pass
            

# if __name__ == "__main__":
#     main()