# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 00:16:08 2020

@author: sinha
"""

import pandas as pd
import os
import time

pd.options.mode.chained_assignment = None
THRESHOLD = 0.1
session_path = "../Sessions/"
ignore_session_id = ["IM177_3"]
session_save_path = session_path + "MediaAnalysis/"
today = time.strftime("%Y-%m-%d")
VIDEO_TYPE = 'V'
 

# def renameDDSegment(df):
#     copy_df = df.copy()
    
#     for i in copy_df.index:
#         if type(copy_df["Type"][i]) == str:
#             if (copy_df["Type"][i] == 'ERT'):
#                 if'DD_F' in copy_df['Delay'][i]:
#                     copy_df['Delay'][i] = copy_df['Delay'][i].replace('DD_F', 'DD_temp')
#                     print (copy_df['Delay'][i])
    
#     print ('\n')
#     for i in copy_df.index:
#         if type(copy_df["Type"][i]) == str:
#             if (copy_df["Type"][i] == 'ERT'):
#                 if'DD_P' in copy_df['Delay'][i]:
#                     copy_df['Delay'][i] = copy_df['Delay'][i].replace('DD_P', 'DD_F')
#                     print (copy_df['Delay'][i])
    
#     print ('\n')
#     for i in copy_df.index:
#         if type(copy_df["Type"][i]) == str:
#             if (copy_df["Type"][i] == 'ERT'):
#                 if'DD_temp' in copy_df['Delay'][i]:
#                     copy_df['Delay'][i] = copy_df['Delay'][i].replace('DD_temp', 'DD_P')
#                     print (copy_df['Delay'][i])
    
#     # temp = copy_df[copy_df['Type'] == 'ERT']
#     # print (temp['Delay'].unique())
#     return pd.DataFrame(copy_df)  

def main():
    if not os.path.exists(session_save_path):
        os.mkdir(session_save_path)
    
    media_analysis_savePath = session_save_path + "MediaAnalysis_" + today + "_" + str(THRESHOLD) + "/" + VIDEO_TYPE + "/"
    
    if not os.path.exists(media_analysis_savePath):
        os.mkdir(media_analysis_savePath)


    session_names = os.listdir(session_path)
    mega = pd.DataFrame()
    mega_avg = pd.DataFrame()
    mega_raw = pd.DataFrame({'PId': [], 'Type': [], 'Start':[], 'End':[], 'HScore':[]})
    
    mega_threshold = pd.DataFrame()
    mega_avg_threshold = pd.DataFrame()
    
    for session_id in session_names:
        # if session_id not in ignore_session_id:
        try:
            print ('\n\n------------- Accessing stats files of ' + session_id + ' for compilation -----------')
            processed_file_path = session_path + session_id + "/processed_data/"
            file_suffix = '_stats.csv'
            avg_suffix = '_AvgStats.csv'
            thresh_suffix = '_threshold.csv'
            thresh_avg_suffix = '_AvgThreshold.csv'
            
            csv = pd.read_csv(processed_file_path + session_id + file_suffix)
            csv_avg = pd.read_csv(processed_file_path + session_id + avg_suffix)
            csv_thresh = pd.read_csv(processed_file_path + session_id + thresh_suffix)
            csv_thresh_avg = pd.read_csv(processed_file_path + session_id + thresh_avg_suffix)
            
            pid = csv['PId'][0]
            eft_ert = csv['Type'][0]
            
            mega = mega.append(csv)
            mega = mega.append(pd.Series(), ignore_index=True)
            mega = mega.append(pd.Series(), ignore_index=True)
            print ('Done appending to the mega csv')
            
            mega_avg = mega_avg.append(csv_avg)
            mega_avg = mega_avg.append(pd.Series(), ignore_index=True)
            mega_avg = mega_avg.append(pd.Series(), ignore_index=True)
            print ('Done appending to the mega avg csv')
            
            mega_threshold = mega_threshold.append(csv_thresh)
            mega_threshold = mega_threshold.append(pd.Series(), ignore_index=True)
            mega_threshold = mega_threshold.append(pd.Series(), ignore_index=True)
            print ('Done appending to the mega Threshold csv')
            
            mega_avg_threshold = mega_avg_threshold.append(csv_thresh_avg)
            mega_avg_threshold = mega_avg_threshold.append(pd.Series(), ignore_index=True)
            mega_avg_threshold = mega_avg_threshold.append(pd.Series(), ignore_index=True)
            print ('Done appending to the mega Threshold avg csv')
            
            raw_file_path = session_path + session_id + "/analysis_data/"
            analysis_folders = os.listdir(raw_file_path)
            
            for sub in analysis_folders:
                raw_file_path = raw_file_path + sub + "/video_analysis_subject.txt"
                raw_csv = pd.read_csv(raw_file_path, sep = ',', names = ['Start', 'End', 'HScore'])
                raw_csv.insert(0, 'PId', pid)
                raw_csv.insert(1, 'Type', eft_ert)
                
                mega_raw = mega_raw.append(raw_csv)
            
            mega_raw = mega_raw.append(pd.Series(), ignore_index = True)
            mega_raw = mega_raw.append(pd.Series(), ignore_index = True)
            mega_raw = mega_raw.append(pd.Series(), ignore_index = True)
            mega_raw = mega_raw.append(pd.Series(), ignore_index = True)
        except:
            pass
    mega = mega.drop(mega.columns[0], axis = 1)
    
    solo_path = media_analysis_savePath + "IntermediateFiles/"
    combined_stats = pd.read_csv(solo_path + 'combined_stats_solo.csv')
    mega = mega.append(pd.Series(), ignore_index = True)
    mega = mega.append(pd.Series(), ignore_index = True)
    mega = mega.append(pd.Series(), ignore_index = True)
    mega = mega.append(combined_stats)
    
    
    output = pd.DataFrame(mega)
    output.to_csv(media_analysis_savePath + 'Video-Stats.csv', index = False)
    print ('\n\nSuccesfully written MEGA csv file')
    
    mega_avg = mega_avg.drop(mega_avg.columns[0], axis = 1)
    combined_stats_smooth = pd.read_csv(solo_path + 'combined_stats_smooth_solo.csv')
    mega_avg = mega_avg.append(pd.Series(), ignore_index = True)
    mega_avg = mega_avg.append(pd.Series(), ignore_index = True)
    mega_avg = mega_avg.append(pd.Series(), ignore_index = True)
    mega_avg = mega_avg.append(combined_stats_smooth)
    
    output_avg = pd.DataFrame(mega_avg)
    output_avg.to_csv(media_analysis_savePath + 'Video-Stats-Smoothed.csv', index = False)
    print ('\n\nSuccesfully written MEGA Avg csv file')
        
    mega_threshold = mega_threshold.drop(mega_threshold.columns[0], axis = 1)
    combined_thresh = pd.read_csv(solo_path + 'combined_thresh_solo.csv')
    mega_threshold = mega_threshold.append(pd.Series(), ignore_index = True)
    mega_threshold = mega_threshold.append(pd.Series(), ignore_index = True)
    mega_threshold = mega_threshold.append(pd.Series(), ignore_index = True)
    mega_threshold = mega_threshold.append(combined_thresh)
    
    output_thresh = pd.DataFrame(mega_threshold)
    output_thresh.to_csv(media_analysis_savePath + 'Video-Thresh.csv', index = False)
    print ('\n\nSuccesfully written MEGA Threshold csv file')
    
    mega_avg_threshold = mega_avg_threshold.drop(mega_avg_threshold.columns[0], axis = 1)
    combined_thresh_smooth = pd.read_csv(solo_path + 'combined_thresh_smooth_solo.csv')
    mega_avg_threshold = mega_avg_threshold.append(pd.Series(), ignore_index = True)
    mega_avg_threshold = mega_avg_threshold.append(pd.Series(), ignore_index = True)
    mega_avg_threshold = mega_avg_threshold.append(pd.Series(), ignore_index = True)
    mega_avg_threshold = mega_avg_threshold.append(combined_thresh_smooth)
    
    output_thresh_avg = pd.DataFrame(mega_avg_threshold)
    output_thresh_avg.to_csv(media_analysis_savePath + 'Video-Thresh-Smoothed.csv', index = False)
    print ('\n\nSuccesfully written MEGA Avg Threshold csv file')
    
    output_raw = pd.DataFrame(mega_raw)
    output_raw.to_csv(media_analysis_savePath + 'Video-Raw.csv', index = False)

if __name__ == "__main__":
    main()