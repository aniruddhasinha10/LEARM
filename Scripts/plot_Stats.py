# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 19:36:54 2020

@author: sinha
"""

import pandas as pd
import os
import numpy as np
import time

import xlsxwriter
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def bar_plotter(eft_values, ert_values, labels, xlabel, ylabel, title, save_path):
    
    width = 0.35  # the width of the bars    
    x = np.arange(len(labels))  # the label locations
    
    fig, ax = plt.subplots(figsize = (15, 10))
    rects1 = ax.bar(x - width/2, eft_values, width, label='EFT')
    rects2 = ax.bar(x + width/2, ert_values, width, label='ERT')
    
    if ylabel == "AVG":  
        ylabel = "AVERAGE"
        ax.set_ylim((0.0, 1.0))
    elif ylabel == "PER": 
        ylabel = "PERCENT"
        ax.set_ylim((0.0, 110.0))
        
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(ylabel, fontsize=15 )
    ax.set_xlabel(xlabel, fontsize=15 )
    ax.set_title(title, fontdict={'fontsize': 16, 'fontweight': 'medium'})
    ax.set_xticks(x)
    ax.set_xticklabels(labels, Rotation = 30, horizontalalignment = "center", fontsize=10 )
    ax.legend()
    
    
    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(round(height,2)),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        rotation = 30,
                        ha='center', va='bottom')
    
    
    autolabel(rects1)
    autolabel(rects2)
    fig.tight_layout()
    plt.savefig(save_path + title + ".png", bbox_inches='tight')
    plt.show()
    

def plotMultiple(eft_data, ert_data, STAT, title, gran, SMOOTH, thresh_int, path):
    # save_path = path + "/BARS/"
    save_path = path

    if not os.path.exists(save_path):
        os.mkdir(save_path)
    
    col_name = "COMBINED"
    title += '-' + gran + '-' + SMOOTH
    
    if SMOOTH != '1':
        col_name += "_Smooth"
        
        
    if thresh_int != '':
        title += '-' + thresh_int
        
    GROUPS = ['C', 'D', 'K']
    filtered_EFT = filter_C_D_K_Data(eft_data)
    filtered_ERT = filter_C_D_K_Data(ert_data)
    
    ylabel = STAT
    xlabel = "Session Segment"
    for g in GROUPS:
        src_eft = filtered_EFT[g]
        src_ert = filtered_ERT[g]
        labels = getLabels_EFR(src_eft, src_ert, g)
        
        title_new = title + '-' + g
        if gran == 'IND':
            # IND_data = src_data.loc[:, src_data.columns != col_name]
            bar_plotter(src_eft, src_ert, labels, xlabel, ylabel, title_new, save_path)
        elif gran == 'CMB':
            bar_plotter(src_eft[col_name], src_ert[col_name], labels, xlabel, ylabel, title_new, save_path)
        
def get_delayLabel(delay):
    delay_mappings = {"1 week-c":"1W", "1 month-c":"1M", "6 month-c":"6M", "1 year-c":"1Y", "2 years-c":"2Y", "5 years-c":"5Y",
                      "1 weekDD_P-c":"1WP", "1 monthDD_P-c":"1MP", "6 monthDD_P-c":"6MP", "1 yearDD_P-c":"1YP", "2 yearsDD_P-c":"2YP","5 yearsDD_P-c":"5YP",
                      "1 weekDD_F-c":"1WF", "1 monthDD_F-c":"1MF", "6 monthDD_F-c":"6MF", "1 yearDD_F-c":"1YF", "2 yearsDD_F-c":"2YF", "5 yearsDD_F-c":"5YF",
                      "N1-c":"N1", "P1-c":"P1", "P2-c":"P2",
                      "1 hour-c":"1H", "4 hours-c":"4H","24 hours-c":"24H","2 days-c":"2D", "4 days-c":"4D",
                      "1 hourDD_F-c":"1HF","4 hoursDD_F-c":"4HF","24 hoursDD_F-c": "24HF","2 daysDD_F-c": "2DF","4 daysDD_F-c":"4DF",
                      "1 hourDD_P-c":"1HP","4 hoursDD_P-c":"4HP","24 hoursDD_P-c":"24HP","2 daysDD_P-c":"2DP","4 daysDD_P-c":"4DP",
                      "N2-c":"N2","N3-c":"N3","P3-c":"P3"}
    return delay_mappings[delay]

def getLabels_EFR(eft_data, ert_data, src):
    eft_labels = eft_data.index.tolist()
    ert_labels = ert_data.index.tolist()
    
    labels = []
    if src == 'K':    
        labels = [src + '-' + get_delayLabel(eft_labels[i]) for i in range(len(eft_labels))]
    else:
        labels = [src + '-' + get_delayLabel(eft_labels[i]) + '-' + get_delayLabel(ert_labels[i]) for i in range(len(eft_labels))]
        
    return labels

def getLabels_EFT(df, src):
    df_labels = df.index.tolist()
        
    labels = []
    if src == 'K':    
        labels = [src + '-' + get_delayLabel(df_labels[i]) for i in range(len(df_labels))]
    else:
        labels = [src + '-' + get_delayLabel(df_labels[i]) for i in range(len(df_labels))]
        
    return labels

def filter_C_D_K_Data(df):
    session_segment = df.index
    
    D_segments = [i for i in session_segment if 'DD_' in i]
    K_segments = ['N1-c', 'P1-c', 'N2-c', 'P2-c', 'N3-c', 'P3-c', 'N4-c', 'P4-c', 'N5-c', 'P5-c']
    
    filtered_data = {}
    D_data = df.loc[df.index.isin(D_segments)]
    K_data = df.loc[df.index.isin(K_segments)]
    C_data = df.loc[(~df.index.isin(K_segments)) & (~df.index.isin(D_segments))]
    
    filtered_data['C'] = C_data
    filtered_data['D'] = D_data
    filtered_data['K'] = K_data
    
    return filtered_data

def plot_CMB(values, x_ticks, ylabel, xlabel, title, save_path):
    
    labels = x_ticks
    values = values.tolist()
    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars
    
    fig, ax = plt.subplots(figsize=(15, 10))
    rects1 = ax.bar(x, values, width)
    
    # Add some text for labels, title and custom x-axis tick labels, etc.
   
    ax.set_title(title, fontdict={'fontsize': 16, 'fontweight': 'medium'})
    
    if ylabel == "AVG":   
        ylabel = "AVERAGE"
        ax.set_ylim((0.0, 1.0))
    elif ylabel == "PER": 
        ylabel = "PERCENT"
        ax.set_ylim((0.0, 110.0))

    ax.set_ylabel(ylabel, fontsize=15 )
    ax.set_xlabel(xlabel, fontsize = 13)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, Rotation = 30, horizontalalignment = "center", fontsize=12 )
    ax.legend()
    
    
    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(round(height, 2)),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 5),  # 3 points vertical offset
                        textcoords="offset points",
                        rotation = 20,
                        ha='center', va='bottom')
    

    autolabel(rects1)
    
    plt.subplots_adjust()
    plt.savefig(save_path + title + ".png", bbox_inches='tight')
    plt.show()
    

def plot_IND(df, x_ticks, ylabel, xlabel, title, save_path):
    
    fig, ax = plt.subplots(figsize=(15, 10))
    df.plot.bar(ax=ax)
    x = np.arange(len(x_ticks))  # the label locations
    ax.set_title(title, fontdict={'fontsize': 10, 'fontweight': 'light'})
    
    
    if ylabel == "AVG": 
        ylabel = "AVERAGE"
        ax.set_ylim((0.0, 1.0))
    elif ylabel == "PER": 
        ylabel = "PERCENT"
        ax.set_ylim((0.0, 110.0))
    
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_xticks(x)
    ax.set_xticklabels(x_ticks, Rotation = 30, horizontalalignment = "center", fontweight='light', fontsize=8)
    ax.legend()

    plt.savefig(save_path + title + ".png", bbox_inches='tight')
    plt.show()
    
def plot_data(data, title, cue_type, stat, gran, smooth, thresh_int, path):
    save_path = path + cue_type + "/"
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    
    title += '-' + stat
    
    ylabel = stat
    xlabel = "Session Segment"

    col_name = 'COMBINED'
    
    title += '-' + gran
    title += '-' + str(smooth)
    
    if smooth != 1:
        col_name += "_Smooth"  
    
    if thresh_int != '':
        title += '-' + thresh_int
        
    GROUPS = ['C', 'D', 'K']
    
    filtered_data = filter_C_D_K_Data(data)
    
    
    for g in GROUPS:
        src_data = filtered_data[g]
        labels = getLabels_EFT(src_data, g)
        labels2 = src_data.columns[:-1]
        # transposed_src_data = src_data.T
        
        # print (labels2, '\n')
        
        title_new = title + '-' + g
        if gran == 'IND':
            IND_data = src_data.loc[:, src_data.columns != col_name]
            plot_IND(IND_data, labels, ylabel, xlabel, title_new+ "_D", save_path)
            
            save_path_IND_session = save_path + "IND_Session/"
            if not os.path.exists(save_path_IND_session):
                os.makedirs(save_path_IND_session)
                
            IND_data_transpose = IND_data.T
            plot_IND(IND_data_transpose, labels2, ylabel, "Session", title_new+ "_S", save_path_IND_session)
            
        elif gran == 'CMB':
            values = src_data[col_name]
            plot_CMB(values, labels, ylabel, xlabel, title_new, save_path)
        
session_path = "../Sessions"
THRESHOLD = 0.1
ignore_session_id = ["IM177_3"]
session_save_path = session_path + "/MediaAnalysis/"
today = time.strftime("%Y-%m-%d")
VIDEO_TYPE = 'V'

if not os.path.exists(session_save_path):
    os.mkdir(session_save_path)
    
media_analysis_savePath = session_save_path + "MediaAnalysis_" + today + "_" + str(THRESHOLD) + "/" + VIDEO_TYPE + "/"
if not os.path.exists(media_analysis_savePath):
    os.mkdir(media_analysis_savePath)

XLS_stats = pd.ExcelFile(media_analysis_savePath + "Video-Stats-Compiled.xlsx")
XLS_stats_smooth = pd.ExcelFile(media_analysis_savePath + "Video-Stats-Smoothed-Compiled.xlsx")
XLS_thresh = pd.ExcelFile(media_analysis_savePath + "Video-Thresh-Compiled.xlsx")
XLS_thresh_smooth = pd.ExcelFile(media_analysis_savePath + "Video-Thresh-Smoothed-Compiled.xlsx")

stats_XLS = [XLS_stats, XLS_stats_smooth]
thresh_XLS = [XLS_thresh,XLS_thresh_smooth]

plot_path = media_analysis_savePath + "/Plots/"

if not os.path.exists(plot_path):
    os.mkdir(plot_path)
    

CUE_TYPES = ['EFT', 'ERT']
STATS_sheets = ['MEANS']
# thresh_val = 0.50
THRESH_sheets = [str(THRESHOLD)+"_SEC_A", str(THRESHOLD)+"_SEC_B"]
DATATYPE = ['V', 'A', 'T']

for cue_type in CUE_TYPES:
    for stat in STATS_sheets:
        sheet = cue_type + "_" + stat
        data = pd.read_excel(XLS_stats, sheet_name=sheet, index_col=0)
        data_smooth = pd.read_excel(XLS_stats_smooth, sheet_name=sheet, index_col=0)
        
        STAT = ''
        if stat == 'MEANS': 
            STAT = 'AVG'
        
        d_type = DATATYPE[0]
        # save_path = plot_path + d_type + "/"
        save_path = plot_path
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        
          
        GRAN = ['IND', 'CMB']
        for gran in GRAN:     
            title_normal = d_type + '-' + cue_type
            plot_data(data, title_normal, cue_type, STAT, gran, 1, '', save_path)
            plot_data(data_smooth, title_normal, cue_type, STAT, gran, 5, '', save_path)
    
    for stat in THRESH_sheets:
        thresh_interval = str(THRESHOLD) + '0_' + stat.split('_')[-1]
        sheet = cue_type + "_" + stat
        thresh = pd.read_excel(XLS_thresh, sheet_name=sheet, index_col=0)
        thresh_smooth = pd.read_excel(XLS_thresh_smooth, sheet_name=sheet, index_col=0)
        
        STAT = 'PER'        
        d_type = DATATYPE[0]
        # save_path = plot_path + d_type + "/"
        save_path = plot_path 
        if not os.path.exists(save_path):
            os.mkdir(save_path)
            
        GRAN = ['IND', 'CMB']
        for gran in GRAN:     
            title_normal = d_type + '-' + cue_type
            plot_data(thresh, title_normal, cue_type, STAT, gran, 1, thresh_interval, save_path)
            plot_data(thresh_smooth, title_normal, cue_type, STAT, gran, 5, thresh_interval, save_path)

for xls in stats_XLS:
    SMOOTH = '1'
    if xls == XLS_stats_smooth:
        SMOOTH = '5'
    for stat in STATS_sheets:
        eft_sheet = 'EFT_' + stat
        ert_sheet = 'ERT_' + stat
        
        eft_data = pd.read_excel(xls, sheet_name=eft_sheet, index_col=0)
        ert_data = pd.read_excel(xls, sheet_name=ert_sheet, index_col=0)
        
        STAT = 'AVG'        
        d_type = DATATYPE[0]
        cue_type = 'EFR'
        
        # save_path = plot_path + d_type + "/EFR/" + STAT + "/" 
        save_path = plot_path + "EFR/" 
        if not os.path.exists(save_path):
            os.makedirs(save_path)
            
        GRAN = ['CMB']
        for gran in GRAN:     
            title_normal = d_type + '-' + cue_type + '-' + STAT
            plotMultiple(eft_data, ert_data, STAT, title_normal, gran, SMOOTH, '', save_path)
            

for xls in thresh_XLS:
    SMOOTH = '1'
    if xls == XLS_thresh_smooth:
        SMOOTH = '5'
    for thresh in THRESH_sheets:
        thresh_interval = str(THRESHOLD) + '0_' + thresh.split('_')[-1]
        eft_sheet = 'EFT_' + thresh
        ert_sheet = 'ERT_' + thresh
        
        eft_data = pd.read_excel(xls, sheet_name=eft_sheet, index_col=0)
        ert_data = pd.read_excel(xls, sheet_name=ert_sheet, index_col=0)
        
        STAT = 'PER'        
        d_type = DATATYPE[0]
        cue_type = 'EFR'
        
        # save_path = plot_path + d_type + "/EFR/" + STAT + "/" 
        save_path = plot_path + "EFR/"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
            
        GRAN = ['CMB']
        for gran in GRAN:     
            title_normal = d_type + '-' + cue_type + '-' + STAT
            plotMultiple(eft_data, ert_data, STAT, title_normal, gran, SMOOTH, thresh_interval, save_path)