# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 18:55:05 2020

@author: sinha
"""

import pandas as pd
import numpy as np
import xlsxwriter

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
     
def compile_eft_ert(writer, data, name):
    cols = data['PId'].unique()
    rows = sorted(list(data['Delay'].unique()))
    
    nScores_data = stats_solo('size', data, rows, cols)
    mean_data = stats_solo('mean', data, rows, cols)
    median_data = stats_solo('median', data, rows, cols)
    std_data = stats_solo('std', data, rows, cols)
    
    data.to_excel(writer, sheet_name = name)
    nScores_data.to_excel(writer, sheet_name = name + "_NSCORES")
    mean_data.to_excel(writer, sheet_name = name + "_MEANS")
    median_data.to_excel(writer, sheet_name = name + "_MEDIANS")
    std_data.to_excel(writer, sheet_name = name + "_STDS")
 
    
def writer_helper(session_path, isAvg, inp_file):
    out_fileName = ''
    if isAvg == 'avg':
        out_fileName = 'compiledMEGA_AvgStats.xlsx'
    else:
        out_fileName = 'compiledMEGA_stats.xlsx'
    writer = pd.ExcelWriter(session_path + out_fileName, engine = 'xlsxwriter')

    mega_stats = pd.read_csv(session_path + inp_file)
    mega_stats = mega_stats.rename(columns = {"mean h_score" : "MeanHScore", 
                                              "std h_score" : "SDHScore", 
                                              "median h_score" : "MedianHScore",
                                              "size" : "NScores"})
    old_eft_stats = mega_stats[mega_stats["Type"] == "EFT"]
    old_ert_stats = mega_stats[mega_stats["Type"] == "ERT"]
    
    compile_eft_ert(writer, old_eft_stats, "EFT")
    compile_eft_ert(writer, old_ert_stats, "ERT")
    
    writer.save()
    writer.close()

session_path = "../Sessions/"
writer_helper(session_path, '', 'mega_stats.csv')
print ('Done writing mega Advanced file')
writer_helper(session_path, 'avg', 'mega_AvgStats.csv')
print ('Done writing mega Advanced Avg file')
