# -*- coding: utf-8 -*-
"""
Created on Fri Aug  6 18:06:42 2020

@author: vignajeeth
"""

import os
import glob
import pandas as pd
from datetime import datetime
import sys

#session_id = "IM177_3"


# Reading data from the csv
def video_info(session_id):

    csv_file_path = "../Sessions/" + session_id + "/session_data/"

    for file in glob.glob(csv_file_path + "*.csv"):
        csv_file_name = os.path.basename(file)

    csv_file_data = pd.read_csv(csv_file_path + csv_file_name)

    time_stamp_videos = csv_file_data.loc[csv_file_data['Video Type'].notnull()][['Date', 'Video Type']]
    time_stamp_videos['Date'] = pd.to_datetime(time_stamp_videos['Date'])
    return(time_stamp_videos)


# Returns the time intervals of all the parts in a session
def time_interval_folder(session_id, date_of_session):

    home_path = os.getcwd()
    analysis_path = "../Sessions/" + session_id + "/analysis_data/"

    os.chdir(analysis_path)

    video_parts_name = [i.split('_')[-2:] for i in sorted(glob.glob('*'))]
    time_format = '%H.%M.%S'
    video_parts_time = [[datetime.combine(date_of_session, datetime.strptime(video_parts_name[j][i], time_format).time()) for i in range(2)]for j in range(len(video_parts_name))]
    video_parts_time = pd.DataFrame(video_parts_time, columns=['Start_Time', 'End_Time'])

    os.chdir(home_path)
    return (video_parts_time)


def returns_happiness_score(session_id, time_stamp_videos, video_parts_time):

    home_path = os.getcwd()
    analysis_folder_path = "../Sessions/" + session_id + "/analysis_data/"
    os.chdir(analysis_folder_path)
    os.chdir(sorted(glob.glob('*'))[-1])

    h_data = pd.read_csv('video_analysis_subject.txt', names=['start', 'end', 'h_score'])

    # Start time of the first N1,P1 - Start time of the last video
    start_index = int((time_stamp_videos.iloc[0][0] - video_parts_time.iloc[-1][0]).total_seconds())
    print('\nStart time from which to extract ' + session_id + ' :' + str(time_stamp_videos.iloc[0][0]))
    print('Start time of the last folder of ' + session_id + ' :' + str(video_parts_time.iloc[-1][0]))
    print('End time of the last folder of  ' + session_id + '  :' + str(video_parts_time.iloc[-1][1]))
    print()
    hp_score = h_data[start_index:][:]

    os.chdir(home_path)
    return(hp_score)


def create_csv(session_id):

    time_stamp_videos = video_info(session_id)
    video_parts_time = time_interval_folder(session_id, time_stamp_videos.iloc[0][0].date())
    hp_score = returns_happiness_score(session_id, time_stamp_videos, video_parts_time)

    home_path = os.getcwd()
    analysis_folder_path = "../Sessions/" + session_id + "/analysis_data/"
    os.chdir(analysis_folder_path)
    os.chdir(sorted(glob.glob('*'))[-1])

    hp_score.to_csv(session_id + '_video_analysis_filtered.csv')

    os.chdir(home_path)


if __name__ == "__main__":
    session_id = str(sys.argv[1])
    create_csv(session_id)
