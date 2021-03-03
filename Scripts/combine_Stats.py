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
        
    output = pd.DataFrame(index = rows, columns = cols)
    
    for delay in rows:
        for pid in cols:
            curr_mean = data[stat][data['PId'] == pid][data['Delay'] == delay]
            curr_mean = curr_mean.tolist()
            if len(curr_mean) != 0:
                output.at[delay, pid] = curr_mean[0]
    return output
     
def compile_eft_ert(data, output_path, name):
    cols = data['PId'].unique()
    rows = sorted(list(data['Delay'].unique()))
    
    mean_data = stats_solo('mean', data, rows, cols)
    median_data = stats_solo('median', data, rows, cols)
    std_data = stats_solo('std', data, rows, cols)
    
    writer = pd.ExcelWriter(output_path + name + '_stats.xlsx', engine = 'xlsxwriter')

    data.to_excel(writer, sheet_name = name)
    mean_data.to_excel(writer, sheet_name = "MEANS")
    median_data.to_excel(writer, sheet_name = "MEDIANS")
    std_data.to_excel(writer, sheet_name = "STDS")
    
    writer.save()
    writer.close()
        
    
    
session_path = "../Sessions/"
mega_stats = pd.read_csv(session_path + 'mega_stats.csv')
mega_stats = mega_stats.rename(columns = {"mean h_score" : "MeanHScore", "std h_score" : "SDHScore", "median h_score" : "MedianHScore"})
old_eft_stats = mega_stats[mega_stats["Type"] == "EFT"]
old_ert_stats = mega_stats[mega_stats["Type"] == "ERT"]

compile_eft_ert(old_eft_stats, session_path, "EFT")
compile_eft_ert(old_ert_stats, session_path, "ERT")


# cols = old_ert_stats['PId'].unique()
# rows = sorted(list(old_ert_stats['Delay'].unique()))

# mean_eft = stats_solo('mean', old_ert_stats, rows, cols)
# median_eft = stats_solo('median', old_ert_stats, rows, cols)
# std_eft = stats_solo('std', old_ert_stats, rows, cols)

