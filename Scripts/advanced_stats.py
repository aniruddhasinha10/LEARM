# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 18:55:05 2020

@author: sinha
"""

import pandas as pd
import os
import numpy as np
import time
import xlsxwriter
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def stats_solo(stat, data, rows, cols): 
    if stat == 'mean':
        stat = "MeanHScore"
    elif stat == 'std':
        stat = "SDHScore"
    elif stat == 'median':
        stat = "MedianHScore"
    elif stat == 'size':
        stat = "NScores"
        
    output = pd.DataFrame(index = rows, columns = cols)
    
    for delay in rows:
        for pid in cols:
            curr_mean = data[stat][data['PId'] == pid][data['Delay'] == delay]
            curr_mean = curr_mean.tolist()
            if len(curr_mean) != 0:
                output.at[delay, pid] = curr_mean[0]
    return output
     
def compile_eft_ert(writer, raw_type, data, name):
    cols = data['PId'].unique()
    delays = data['Delay'].copy()
    delays = delays.apply(lambda x: x.split('-')[0] + '-c')
    rows = list(delays.unique())
    
    nScores_data = stats_solo('size', data, rows, cols)
    mean_data = stats_solo('mean', data, rows, cols)
    median_data = stats_solo('median', data, rows, cols)
    std_data = stats_solo('std', data, rows, cols)
    
    data.to_excel(writer, sheet_name = name)
    nScores_data.to_excel(writer, sheet_name = name + "_NSCORES")
    mean_data.to_excel(writer, sheet_name = name + "_MEANS")
    median_data.to_excel(writer, sheet_name = name + "_MEDIANS")
    std_data.to_excel(writer, sheet_name = name + "_STDS")
    raw_type.to_excel(writer, sheet_name = name + "_RAW")
 
def writer_helper(session_path, isAvg, inp_file):
    out_fileName = ''
    if isAvg == 'avg':
        out_fileName = 'Video-Stats-Smoothed-Compiled.xlsx'
    else:
        out_fileName = 'Video-Stats-Compiled.xlsx'
    writer = pd.ExcelWriter(session_path + out_fileName, engine = 'xlsxwriter')
    
    raw_data = pd.read_csv(raw_file)
    raw_eft = raw_data[raw_data["Type"] == "EFT"]
    raw_ert = raw_data[raw_data["Type"] == "ERT"]
    mega_stats = pd.read_csv(session_path + inp_file)
    mega_stats = mega_stats.rename(columns = {"mean h_score" : "MeanHScore", 
                                              "std h_score" : "SDHScore", 
                                              "median h_score" : "MedianHScore",
                                              "size" : "NScores"})
    old_eft_stats = mega_stats[mega_stats["Type"] == "EFT"]
    old_ert_stats = mega_stats[mega_stats["Type"] == "ERT"]
    
    compile_eft_ert(writer, raw_eft, old_eft_stats, "EFT")
    compile_eft_ert(writer, raw_ert, old_ert_stats, "ERT")
    
    writer.save()
    writer.close()
    
def filterThresh_solo(stat, data, rows, cols): 
    output = pd.DataFrame(index = rows, columns = cols)
    
    for delay in rows:
        for pid in cols:
            curr_data = data[stat][data['PId'] == pid][data['Delay'] == delay]
            curr_data = curr_data.tolist()
            if len(curr_data) != 0:
                output.at[delay, pid] = curr_data[0]
    return output
     
def compile_threshold(writer, data, name, isAvg, path):
    cols = data['PId'].unique()
    delays = data['Delay'].copy()
    
    # Keep only the "-c" delays
    delays = delays.apply(lambda x: x.split('-')[0] + '-c')
    rows = list(delays.unique())
    
    nScores_data = filterThresh_solo('NScores', data, rows, cols)
    aboveThreshSecondData = filterThresh_solo('aboveThreshPerSec', data, rows, cols)
    belowThreshSecondData = filterThresh_solo('belowThreshPerSec', data, rows, cols)
    
    data.to_excel(writer, sheet_name = name)
    nScores_data.to_excel(writer, sheet_name = name + "_NSCORES")
    aboveThreshSecondData.to_excel(writer, sheet_name = name + "_"+str(THRESHOLD)+"_SEC_A")
    belowThreshSecondData.to_excel(writer, sheet_name = name + "_"+str(THRESHOLD)+"_SEC_B")


def threshold_writer_helper(session_path, isAvg, inp_file):
    out_fileName = ''
    if isAvg == 'avg':
        out_fileName = 'Video-Thresh-Smoothed-Compiled.xlsx'
    else:
        out_fileName = 'Video-Thresh-Compiled.xlsx'
    thresh_writer = pd.ExcelWriter(session_path + out_fileName, engine = 'xlsxwriter')
    
    thresh_stats = pd.read_csv(session_path + inp_file)
    old_eft_thresh_stats = thresh_stats[thresh_stats["Type"] == "EFT"]
    old_ert_thresh_stats = thresh_stats[thresh_stats["Type"] == "ERT"]
    
    compile_threshold(thresh_writer, old_eft_thresh_stats, "EFT", isAvg, session_path)
    compile_threshold(thresh_writer, old_ert_thresh_stats, "ERT", isAvg, session_path)
    
    thresh_writer.save()
    thresh_writer.close()

session_path = "../Sessions/"
THRESHOLD = 0.1
ignore_session_id = ["IM177_3"]
session_save_path = session_path + "MediaAnalysis/"
today = time.strftime("%Y-%m-%d")
VIDEO_TYPE = 'V'

if not os.path.exists(session_save_path):
    os.mkdir(session_save_path)
    
media_analysis_savePath = session_save_path + "MediaAnalysis_" + today + "_" + str(THRESHOLD) + "/" + VIDEO_TYPE + "/"

if not os.path.exists(media_analysis_savePath):
    os.mkdir(media_analysis_savePath)


raw_file = media_analysis_savePath + "Video-Raw.csv"
writer_helper(media_analysis_savePath, '', 'Video-Stats.csv')
print ('Done writing mega Advanced file')
writer_helper(media_analysis_savePath, 'avg', 'Video-Stats-Smoothed.csv')
print ('Done writing mega Advanced Avg file')

threshold_writer_helper(media_analysis_savePath, '', 'Video-Thresh.csv')
print ('Done writing mega Advanced Threshold file')
threshold_writer_helper(media_analysis_savePath, 'avg', 'Video-Thresh-Smoothed.csv')
print ('Done writing mega Advanced Avg Threshold file')


