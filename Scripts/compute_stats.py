# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 04:32:02 2020

@author: sinha
"""

import pandas as pd
import os
import numpy as np
import time

pd.options.mode.chained_assignment = None 
    

def calculate_runningAvg(df, prev_len):
    original_df = df.copy()
    for i in range(prev_len, prev_len + len(df)-4):
        original_df.at[i, 'h_score'] = np.mean(original_df.loc[i:i+4, 'h_score'])
    
    return pd.DataFrame(original_df)

def merge_Segments(seg_df, prev_len):
    d_segments = seg_df['Segment'].unique()
        
    seg_df['Delay'] = seg_df['Delay'].apply(lambda x: x.split('-')[0])    
    n_seg = 1
    
    d = seg_df['Delay'][prev_len]

    original = seg_df.loc[seg_df['Delay'] == d].copy()
    
    for seg in d_segments:
        original.loc[original['Segment'] == seg, 'Delay'] = original['Delay'] + '-' + str(n_seg)
        n_seg += 1
    
        
    original.reset_index(drop = True)
    
    avg_seg_df = calculate_runningAvg(original, prev_len)
    
    avg_seg_df.reset_index(drop = True)

    return original, avg_seg_df

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
    original = csv.copy()
    delays = csv['Delay'].unique()
    # print (delays)
    
    df = pd.DataFrame()
    df_avg = pd.DataFrame()
    prev_len = 0
    
    for d in delays:
        d_hscores = csv.loc[csv['Delay'] == d]
        original_avg_df = calculate_runningAvg(original.loc[original['Delay'] == d], prev_len)
        merged, merged_avg = merge_Segments(d_hscores, prev_len)
        
        prev_len += len(d_hscores)
        
        df = df.append(original.loc[original['Delay'] == d])
        df = df.append(merged)
        
        df_avg = df_avg.append(original_avg_df)
        df_avg = df_avg.append(merged_avg)
   
    df.reset_index(drop=True)
    df_avg.reset_index(drop=True)    
    df = delete_columns(df)
    # print (df['Delay'])
    df_avg = delete_columns(df_avg)
    return df, df_avg

def threshold_values(df):
    delays = df['Delay'].unique()
    dfg = df.copy()
    
    threshold_df = dfg.groupby('Delay').mean().copy()
    aboveThreshPerSec, belowThreshPerSec = [], []
    DELAY, df_size = [], []
    
    for d in delays:
        DELAY.append(d)
        values = dfg.loc[dfg['Delay'] == d, 'h_score'].tolist()
        
        n_below_sec = len([i for i in values if i < THRESHOLD])
        n_above_sec = len([i for i in values if i >= THRESHOLD])
        size_sec = len(values)
        
        min_vals = []
        for i in range(len(values)-60):
            min_vals.append(np.mean(values[i:i+60]))
        
        df_size.append(size_sec)
        
        belowThreshPerSec.append( round(n_below_sec*100/size_sec, 2) )
        aboveThreshPerSec.append( round(n_above_sec*100/size_sec, 2) )
        
    threshold_df['NScores'] = df_size
    threshold_df['Threshold'] = THRESHOLD
    threshold_df['aboveThreshPerSec'] = aboveThreshPerSec
    threshold_df['belowThreshPerSec'] = belowThreshPerSec
    threshold_df = threshold_df.drop(['h_score'], axis = 1)
    threshold_df.reset_index(drop=True, inplace = True)
    threshold_df.reset_index(drop=True, inplace = True)
    threshold_df.insert(0, 'Delay', DELAY)

    return pd.DataFrame(threshold_df)              
    
def compute_statistics(df):
    dfg = df.copy()
    delays = dfg['Delay'].unique().tolist()
    d_map = {}
    i_map = {}
    for i,d in enumerate(delays):
        if i < 10:
            d_map[d] = '0' + str(i)
            i_map['0'+str(i)] = d
        else:
            d_map[d] = str(i)
            i_map[str(i)] = d
    
    dfg['Delay'] = dfg['Delay'].apply(lambda x: d_map[x])
    
    stats = dfg.groupby('Delay').mean()
    sizes = dfg.groupby('Delay').size().tolist()
    df_std = dfg.groupby('Delay').std()['h_score']
    df_median = dfg.groupby('Delay').median()['h_score']
    
    stats['mean h_score'] = round(stats['h_score'], 4)
    stats['std h_score'] = round(df_std, 4)
    stats['median h_score'] = round(df_median, 4)
    stats['size'] = sizes
    
    stats = stats.drop(['h_score'], axis = 1)
    stats.reset_index(level=0, inplace = True)
    stats['Delay'] = stats['Delay'].apply(lambda x: i_map[x])

    return stats

def helper(csv, pid, eft_ert_type, isThreshold):
    if isThreshold:
        csv.reset_index(level=0, inplace = True)
        
    csv.insert(0, 'PId', pid)
    csv.insert(1, 'Type', eft_ert_type)
    csv.set_index('PId')
    if 'index' in csv.columns:
        del(csv['index'])
    
    output = pd.DataFrame(csv)
    output.set_index('PId')
    
    return output

def appendCombinedData(stats, thresh, csv, eft_ert_type):
    original = csv.copy()
    
    delays = original['Delay'].unique()
    
    # Create the dictionary for STATS data
    for d in delays:
        values = original.loc[original['Delay'] == d, 'h_score'].tolist()
        if d not in stats[eft_ert_type]:
            stats[eft_ert_type][str(d)] = []
        stats[eft_ert_type][str(d)].extend(values)
    # Create the dictionary for Threshold Data
    for d in delays:
        values = original.loc[original['Delay'] == d, 'h_score'].tolist()
        if d not in thresh[eft_ert_type]:
            thresh[eft_ert_type][str(d)] = [0 for i in range(3)]
        n_below = len([i for i in values if i < THRESHOLD])
        n_above = len([i for i in values if i >= THRESHOLD])
        size = len(values)
        
        thresh[eft_ert_type][str(d)][0] += size
        thresh[eft_ert_type][str(d)][1] += n_below
        thresh[eft_ert_type][str(d)][2] += n_above
    
    return

def createCombinedStatsData(cols, combined, isAvg):
    df = pd.DataFrame(columns = cols)
    PId = 'COMBINED'
    if isAvg:
        PId += '_Smooth'
    for eft_name in combined:
        temp_df = pd.DataFrame(columns = cols)
        if len(combined[eft_name]) > 0:
            temp_df['PId'] = [PId for _ in range(len(combined[eft_name].keys()))]
            temp_df['Type'] = eft_name
            temp_df['Delay'] = list(combined[eft_name].keys())
            temp_df['mean h_score'] = [np.mean(elem) for elem in combined[eft_name].values()]
            temp_df['std h_score'] = [np.std(elem) for elem in combined[eft_name].values()]
            temp_df['median h_score'] = [np.median(elem) for elem in combined[eft_name].values()]
            temp_df['size'] = [len(elem) for elem in combined[eft_name].values()]
        
            df = df.append(temp_df)
    df = df.reset_index()
    df.drop(['index'], axis = 1, inplace=True)
    return df


def createCombinedThreshData(cols, combined, isAvg):
    df = pd.DataFrame(columns = cols)
    PId = 'COMBINED'
    if isAvg:
        PId += '_Smooth'
    for eft_name in combined:
        temp_df = pd.DataFrame(columns = cols)
        if len(combined[eft_name]) > 0:
            temp_df['PId'] = [PId for _ in range(len(combined[eft_name].keys()))]
            temp_df['Type'] = eft_name
            temp_df['Delay'] = list(combined[eft_name].keys())
            temp_df['NScores'] = [elem[0] for elem in combined[eft_name].values()]
            temp_df['Threshold'] = THRESHOLD
            temp_df['aboveThreshPerSec'] = [round((elem[2]*100/elem[0]), 2) for elem in combined[eft_name].values()]
            temp_df['belowThreshPerSec'] = [round((elem[1]*100/elem[0]), 2) for elem in combined[eft_name].values()]
        
            df = df.append(temp_df)
    df = df.reset_index()
    df.drop(['index'], axis = 1, inplace=True)
    return df

THRESHOLD = 0.1
session_path = "../Sessions/"
ignore_session_id = ["IM177_3"]
session_save_path = session_path + "MediaAnalysis/"
today = time.strftime("%Y-%m-%d")
VIDEO_TYPE = 'V'


def renameDDSegment(df):
    copy_df = df.copy()
    
    for i in copy_df.index:
        if type(copy_df["Type"][i]) == str:
            if (copy_df["Type"][i] == 'ERT'):
                if'DD_F' in copy_df['Delay'][i]:
                    copy_df['Delay'][i] = copy_df['Delay'][i].replace('DD_F', 'DD_temp')
                    # print (copy_df['Delay'][i])
    
    # print ('\n')
    for i in copy_df.index:
        if type(copy_df["Type"][i]) == str:
            if (copy_df["Type"][i] == 'ERT'):
                if'DD_P' in copy_df['Delay'][i]:
                    copy_df['Delay'][i] = copy_df['Delay'][i].replace('DD_P', 'DD_F')
                    # print (copy_df['Delay'][i])
    
    # print ('\n')
    for i in copy_df.index:
        if type(copy_df["Type"][i]) == str:
            if (copy_df["Type"][i] == 'ERT'):
                if'DD_temp' in copy_df['Delay'][i]:
                    copy_df['Delay'][i] = copy_df['Delay'][i].replace('DD_temp', 'DD_P')
                    # print (copy_df['Delay'][i])
    
    return pd.DataFrame(copy_df)  

def main():
    if not os.path.exists(session_save_path):
        os.mkdir(session_save_path)
    
    media_analysis_savePath = session_save_path + "MediaAnalysis_" + today + "_" + str(THRESHOLD) + "/" + VIDEO_TYPE + "/"
    
    if not os.path.exists(media_analysis_savePath):
        os.makedirs(media_analysis_savePath)
        
    solo_path = media_analysis_savePath + "IntermediateFiles/"
    if not os.path.exists(solo_path):
        os.mkdir(solo_path)
        
    thresh_columns = []
    stats_columns = []
    stats_combined = {'EFT':{},
                      'ERT':{}}
    stats_smooth_combined = {'EFT':{},
                             'ERT':{}}
    
    thresh_all = {'EFT':{},
                'ERT':{}}
    thresh_smooth_all = {'EFT':{},
                       'ERT':{}}
    first_thresh = True
    first_stats = True
    
    session_names = os.listdir(session_path)
    log_file = open('LOGS_computeStats.txt', 'w+')
    for session_id in session_names:
        # if session_id not in ignore_session_id:
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
            print ('Starting thresh')
            thresholded = threshold_values(filtered_csv)
            thresholded_avg = threshold_values(filtered_avg_csv)
            thresh_output = helper(thresholded, pid, eft_ert_type, False)
            thresh_output_avg = helper(thresholded_avg, pid, eft_ert_type, False)
            
            
            print ('Completed Thresh')
            stats = compute_statistics(filtered_csv)
            output = helper(stats, pid, eft_ert_type, True)
            stats_avg = compute_statistics(filtered_avg_csv)
            output_avg = helper(stats_avg, pid, eft_ert_type, True)
            
            
            if first_thresh:
                thresh_columns = thresh_output.columns
                first_thresh = False
                
            appendCombinedData(stats_combined, thresh_all, filtered_csv, eft_ert_type)
            
            
            if first_stats:
                stats_columns = output.columns
                first_stats = False
                
            appendCombinedData(stats_smooth_combined, thresh_smooth_all, filtered_avg_csv, eft_ert_type)
            
            if eft_ert_type == 'ERT':
                output = renameDDSegment(output)
                output_avg = renameDDSegment(output_avg)
                thresh_output = renameDDSegment(thresh_output)
                thresh_output_avg = renameDDSegment(thresh_output_avg)
            
            print ('writing')
            output.to_csv(processed_file_path + '/' + session_id + '_stats.csv')
            output_avg.to_csv(processed_file_path + '/' + session_id + '_AvgStats.csv')
            
            thresh_output.to_csv(processed_file_path + '/' + session_id + '_threshold.csv')
            thresh_output_avg.to_csv(processed_file_path + '/' + session_id + '_AvgThreshold.csv')
            print ('Written successfully\n')
            
            log_file.write(session_id + " | " +  " successfully written. No ISSUES.\n\n")
            
        except Exception as e:
            print (e)
            log_file.write(session_id + " | " + "ERROR:::: " + str(e) + " | " + " didn't execute correctly. \n\n")
    
    
    combined_stats_data = createCombinedStatsData(stats_columns, stats_combined, False)
    combined_stats_data.to_csv(solo_path + 'combined_stats_solo.csv')
    
    combined_stats_smoothed = createCombinedStatsData(stats_columns, stats_smooth_combined, True)
    combined_stats_smoothed.to_csv(solo_path + 'combined_stats_smooth_solo.csv')
        
    combined_thresh_data = createCombinedThreshData(thresh_columns, thresh_all, False)
    combined_thresh_data.to_csv(solo_path + 'combined_thresh_solo.csv')
    
    combined_thresh_smoothed = createCombinedThreshData(thresh_columns, thresh_smooth_all, True)
    combined_thresh_smoothed.to_csv(solo_path + 'combined_thresh_smooth_solo.csv')
    

if __name__ == "__main__":
    main()