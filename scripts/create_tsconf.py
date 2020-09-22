# -*- coding: utf-8 -*-
"""
Created on Thu May  7 02:27:39 2020

@author: sinha
"""

# -*- coding: utf-8 -*-
"""
Created on Wed May  6 22:46:35 2020

@author: Aniruddha Sinha
"""
from io import BytesIO
from xml.dom import minidom
import datetime
import xml.etree.ElementTree as ET

"""
function reads config data from config.txt file
"""

def read_config():
    configs = []
    with open('./config.txt','r') as config:
        configs = config.read().split('\n')
    media_file_names = []
    media_file_formats = []
    rel_media_paths=[]

    for config in configs:
        if any(c.isalpha() for c in config):
            if "vid_file" in config[:8]:
                splits = config.split(' | ')
                temp = splits[1].split('/', 3)[3]

                link_url="../../"+temp
                media_file_names.append(link_url)
                rel_url = link_url
                rel_media_paths.append(rel_url)

                if ".mp4" in temp.split('/')[-1]:
                    media_file_formats.append("video/mp4")

    analysis_names = []
    analysis_files = []
    rel_analysis_paths = []
    for config in configs:
        if any(c.isalpha() for c in config):
            if "analysis" in config:
                splits = config.split(' | ')
                analysis_names.append(splits[0].strip())

                analysis_path = splits[1].strip().split('/')[-1]
                analysis_files.append(analysis_path)
                rel_analysis_paths.append('./' + analysis_path)

    return [media_file_names,media_file_formats,
            rel_media_paths,analysis_names,
            analysis_files, rel_analysis_paths]


"""
function forms the annotation tag
"""
def form_annotation():
    d = datetime.datetime.today()
    time = str(d.time()).split('.')[0]
    dict1 = {"date":str(d.date())+'T'+time+'-05:00',
             "version":"1.0",
             }

    return dict1

"""
function forms the header section in final eaf file
"""
def form_tracksource(time_series):
    analysis_files = [file for item in read_config()[4:5] for file in item]
    print (analysis_files)
    indx = 0
    for key, value in sentiment_dict.items():
        tracksource_tag = ET.SubElement(time_series,"tracksource")
        tracksource_tag.set("sample-type","Discontinuous Rate")
        tracksource_tag.set("source-url", key + "_subject.txt")
#        tracksource_tag.set("source-url", analysis_files[indx])
        indx += 1
        
        tracksource_tag.set("time-column", "0")
        
        property_tag = ET.SubElement(tracksource_tag, "property")
        property_tag.set("key", "provider")
        property_tag.set("value", "mpi.eudico.client.annotator.timeseries.csv.CSVServiceProvider")
        
        track_tag = ET.SubElement(tracksource_tag, "track")
        track_tag.set("derivative", "0")
        track_tag.set("name", value[0])
        
        track_property_tag = ET.SubElement(track_tag, "property")
        track_property_tag.set("key", "detect-range")
        
        if key is "text_analysis":
            track_property_tag.set("value", "false");
        else:
            track_property_tag.set("value", "true");
        
        sample_position_tag = ET.SubElement(track_tag, "sample-position")
        pos_tag = ET.SubElement(sample_position_tag, "pos")
        pos_tag.set("col", "2")
        pos_tag.set("row", "0")
        
        description_tag = ET.SubElement(track_tag, "description")
        units_tag = ET.SubElement(track_tag, "units")
        range_tag = ET.SubElement(track_tag, "range")
        range_tag.set("max", value[1])
        range_tag.set("min", value[2])
        color_tag = ET.SubElement(track_tag, "color")
        color_tag.text = value[3]
        
    return time_series

sentiment_dict = {"text_analysis": ["Text Sentiment",
                                    "100.0",
                                   "0.0",
                                   "204,0,0"],
                "audio_analysis": ["Audio Sentiment",
                                   "1.0",
                                   "1.3731778E-9",
                                   "0,0,204"],
                "video_analysis": ["Video Sentiment",
                                   "0.338",
                                   "0.0",
                                   "0,204,0"],
                    }

def main():
    time_series = ET.Element('timeseries',form_annotation())
    for key,value in form_annotation().items():
        time_series.set(key,value)
    
    time_series = form_tracksource(time_series)
    
    tree = ET.ElementTree(time_series)
    f = BytesIO()
    tree.write(f, encoding="UTF-8", xml_declaration = True)
    
    tsconf_name = "./" + read_config()[0][0].split('/')[-1].split('.')[0] + "_tsconf.xml"
    with open(tsconf_name, "wb") as f1:
        f1.write(str.encode(minidom.parseString(f.getvalue()).toprettyxml(indent="   ")))


if __name__ == "__main__":
    main()
