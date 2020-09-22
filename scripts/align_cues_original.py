# -*- coding: utf-8 -*-
"""
Created on Wed May  6 22:46:35 2020

@author: sinha
"""
import csv
import os
from datetime import datetime

def find_startTimes(subject_media_path):
    vid_file_times = []
    vid_names = []
    for vid_file in os.listdir(subject_media_path):
        vid_file_name, vid_file_ext = os.path.splitext(vid_file)
        
        if (vid_file_ext == '.mp4'):
            vid_names.append(vid_file_name)
            
            vid_file_timestamp = return_dateTime_timestamped(vid_file_name)
            vid_file_times.append(vid_file_timestamp)      
    return vid_file_times, vid_names
    
def return_dateTime_timestamped(vid_file_name):
    months = {'Jan': '01',
              'Feb': '02',
              'Mar': '03',
              'Apr': '04',
              'May': '05',
              'Jun': '06',
              'Jul': '07',
              'Aug': '08',
              'Sep': '09',
              'Oct': '10',
              'Nov': '11',
              'Dec': '12'}
    
    filename_parts = vid_file_name.split('_')
    month = filename_parts[4]
    
    vid_dateTime = months[month] + '/' + filename_parts[5] + '/' + filename_parts[6] + ' '
    for num in filename_parts[7].split('.'):
        vid_dateTime = vid_dateTime + num + ':'
    
    vid_dateTime = vid_dateTime[:-1]
    vid_timestamp = datetime.strptime(vid_dateTime, '%m/%d/%Y %H:%M:%S').timestamp()
    
    return vid_timestamp
    
path = "../Sessions/IM203_23/session_data/"
subject_media_path = path + "subject_media/processedVideos/"

start_timestamps, vid_names = find_startTimes(subject_media_path)
print (start_timestamps, vid_names)
all_files = os.listdir(path)

save_path = os.path.split(os.path.split(path)[0])[0]

for file in all_files:
    filename = os.path.splitext(file)[0]
    ext = os.path.splitext(file)[1]
    if (ext == '.csv'):
        f = open(path + file)
        csvreader = csv.reader(f, delimiter = ',')
        
        delays = []
        date_time = []
        cue = []
        last_sentiments = []
        count = 0
        for row in csvreader:
            delay = row[3:4][0]
            video_type = row[-1]  
            if (count == 0):             
                count += 1
                continue
            date_time.append(row[2:3][0])
            
            if (video_type == ""):
                cue.append(row[5:6][0])
                delays.append(delay)
            else:
                cue.append(video_type)
                delays.append(video_type)
            last_sentiments.append(row[9:10])

        # print (len(date_time), len(cue), len(last_sentiments), len(delays))
        # print (delays)
        new_date_time = []
        timestamps = []
        for item in date_time:
#            print('\n', item)
            elements = item.split(',')

            am_pm = elements[1].split()[1]
            time_values = elements[1].split()[0].split(':')
            hr, minute, sec = time_values
            if (am_pm == 'PM'):
                hr = str( int(hr) + 12 )
                
            time_values = hr + ':' + minute + ':' + sec
            
            new_item = elements[0] + ' ' + time_values
            timestamp = datetime.strptime(new_item, '%m/%d/%Y %H:%M:%S').timestamp()
#            print (timestamp)
            new_date_time.append ( new_item )
            timestamps.append(timestamp)
        
        start_ts = start_timestamps[0]
        # start_ts = timestamps[0]
        
        # print (new_start_ts < start_ts)
        
        output1 = open (save_path + '/' + vid_names[0] + '_cueTimestamped.csv', 'w+')
        output1_txt = open (save_path + '/' + vid_names[0] + '_cueTimestamped.txt', 'w+')
        
        output2 = ""
        output2_txt = ""
        
        if len(vid_names) > 1:
            output2 = open (save_path + '/' + vid_names[1] + '_cueTimestamped.csv', 'w+')
            output2_txt = open (save_path + '/' + vid_names[1] + '_cueTimestamped.txt', 'w+')
        
        prev_delay = "-1"
        last_ts = 0
        first_ts = 0
        first_ts = timestamps[0] - start_ts
        last_cue = ""
        
        NP_CUES = ['N1', 'P1', 'N2', 'P2', 'N3', 'P3', 'N4', 'P4', 'N5', 'P5']
        
        cue_end = False
        for i in range(len(delays)):
            curr_ts = timestamps[i]
            if (len(start_timestamps) > 1 and curr_ts > start_timestamps[1]):
                start_ts = start_timestamps[1]
                
            # first_ts = curr_ts - start_ts
            next_delay = delays[i]
            
            if (next_delay == prev_delay):
                cue_end = True
                last_ts = curr_ts - start_ts
                if (cue[i] != ""):
                    last_cue = cue[i]
#                    print (last_cue)
            else:
                if (cue_end):
                    cue_end = False
                    write_text = str(first_ts) + "," + str(last_ts) + "," + last_cue + "\n"
                    # print (last_cue, '\n')
                    print (last_cue in NP_CUES, output2 != "", output2_txt != "")
                    if (last_cue in NP_CUES and output2 != "" and output2_txt != ""):
                        output2.write(write_text)
                        output2_txt.write(write_text)
                    else:
                        output1.write(write_text)
                        output1_txt.write(write_text)
                
                first_ts = curr_ts - start_ts
                prev_delay = next_delay
        
        # print(last_cue)        
        write_text = str(first_ts) + "," + str(last_ts) + "," + last_cue + "\n"
        if (last_cue in NP_CUES and output2 != "" and output2_txt != ""):
            output2.write(write_text)
            output2_txt.write(write_text)
        else:
            output1.write(write_text)
            output1_txt.write(write_text)
        
        output1.close()
        output1_txt.close()
        
        if (output2 != "" and output2_txt != ""):
            output2.close()
            output2_txt.close()
                
        


#path = ""
#
#def set_file_path(file_path):
#    global path
#    path = file_path  
#
#def get_file_path():
#    global path
#    return path
#
#curr_config_file_path = "../Sessions/IM175_1/IM175_1_part-1_video_Nov_25_2019_18.10.00_18.28.31.txt"
#set_file_path(curr_config_file_path)
#print(get_file_path())
##form_eaf
#
#session_id = curr_config_file_path.split("/")[2]
#configs = []
#with open(curr_config_file_path,'r') as config:
#    configs = config.read().split('\n')
#media_file_names = []
#media_file_formats = []
#rel_media_paths=[]
#
#for config in configs:
#    if any(c.isalpha() for c in config):
#        if "vid_file" in config[:8]:
#            splits = config.split(' | ')
#            temp = splits[1]
#
#            link_url = temp
#            print(link_url)
#            media_file_names.append(link_url)
#            rel_url = "../../" + session_id + "/" + link_url
#            rel_media_paths.append(rel_url)
#
#            if ".mp4" in temp.split('/')[-1]:
#                media_file_formats.append("video/mp4")
#
#analysis_names = []
#analysis_files = []
#rel_analysis_paths = []
#for config in configs:
#    if any(c.isalpha() for c in config):
#        if "analysis" in config:
#            splits = config.split(' | ')
#            analysis_names.append(splits[0].strip())
#            
#            analysis_path = splits[1].strip()
#            analysis_files.append(analysis_path)
#            rel_analysis_paths.append('../' + session_id + "/" + analysis_path)
#            
#arr = [media_file_names,media_file_formats,
#            rel_media_paths,analysis_names,
#            analysis_files, rel_analysis_paths]
#
##'../../'arr[0][0].split('/')[-1].split('.')[0] + ".eaf"
#an = [x for item in arr[4:5] for x in item]


#from io import BytesIO
#from xml.etree import ElementTree as ET
#
#document = ET.Element('outer')
#node = ET.SubElement(document, 'inner')
#et = ET.ElementTree(document)
#
#f = BytesIO()
#et.write(f, encoding="UTF-8", xml_declaration=True) 
#print(f.getvalue())  # your XML file, encoded as UTF-8