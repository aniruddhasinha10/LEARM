# -*- coding: utf-8 -*-
"""
Created on Wed May 13 16:34:05 2020

@author: sinha
"""

from io import BytesIO
from xml.dom import minidom
import datetime
import xml.etree.ElementTree as ET

import os

session_path = "../Sessions/"

######################################### READING CONFIG FILE FOR GENERATION OF EAF AND TSCONF ##################################################
"""
function reads config data from config.txt file
"""
def read_config(_file):
    session_id = _file.split("/")[2]
    config_file = _file + ".txt"
    configs = []
    
    config = open(config_file, "r")
    configs = config.read().split('\n')
    
    media_file_names = []
    media_file_formats = []
    rel_media_paths=[]

    for config in configs:
        if any(c.isalpha() for c in config):
            if "vid_file" in config[:8]:
                splits = config.split(' | ')
                temp = splits[1]
    
                link_url = temp
                media_file_names.append(link_url)
                rel_url = "./" + link_url
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
                
                analysis_path = splits[1].strip()
                analysis_files.append(analysis_path)
                rel_analysis_paths.append("./" + analysis_path)
                
    return [media_file_names,media_file_formats,
            rel_media_paths,analysis_names,
            analysis_files, rel_analysis_paths]

#################################################################################################################################

'''
-------------------------------------------------------
START OF FUNCTIONS FOR CREATING EAF FILE 
-------------------------------------------------------
'''

"""
fucntion adds the tags for specifying media files
"""
def add_media(header_tag,files):
    for i in range(len(files[0])):
        media_descriptor = ET.SubElement(header_tag,"MEDIA_DESCRIPTOR")
        media_descriptor.set("MEDIA_URL", "file:///" + files[0][i])
        media_descriptor.set("MIME_TYPE",files[1][i])
        media_descriptor.set("RELATIVE_MEDIA_URL",files[2][i])
    return header_tag

"""
fucntion adds the tags for specifying linked analysis files
"""
def add_linked_file(header_tag, files, eaf_name):
    for i in range(len(files[0])):
        linked_file_descriptor = ET.SubElement(header_tag,"LINKED_FILE_DESCRIPTOR")
        linked_file_descriptor.set("LINK_URL", "file:///" + files[1][i])
        linked_file_descriptor.set("MIME_TYPE","text/plain")
        linked_file_descriptor.set("RELATIVE_LINK_URL",files[2][i])
    
    linked_file_descriptor = ET.SubElement(header_tag,"LINKED_FILE_DESCRIPTOR")
    
    
    tsconf_name = eaf_name.split("/")[-1] + "_tsconf.xml"
#    print(tsconf_name)
    linked_file_descriptor.set("LINK_URL", tsconf_name)
    linked_file_descriptor.set("MIME_TYPE","text/xml")
    linked_file_descriptor.set("RELATIVE_LINK_URL", "./" + tsconf_name)
    
    return header_tag


"""
function forms the header section in final eaf file
"""
def form_header(annotation_document, eaf_name):
    header_tag = ET.SubElement(annotation_document,"HEADER")
    header_tag.set("MEDIA_FILE","")
    header_tag.set("TIME_UNITS","milliseconds")
    header_tag = add_media(header_tag, read_config(eaf_name)[:3])
    header_tag = add_linked_file(header_tag, read_config(eaf_name)[3:], eaf_name)

#    property_1 = ET.SubElement(header_tag,"PROPERTY")
#    property_1.set("NAME","URN")
#    property_1.text = "urn:nl-mpi-tools-elan-eaf:298594aa-e982-4e4a-aae2-fa40fca12994"
#    property_2 = ET.SubElement(header_tag,"PROPERTY")
#    property_2.set("NAME","lastUsedAnnotationId")
#    property_2.text = "0"
#    annotation_document = add_timeorder_eaf(annotation_document)
    return annotation_document
#    return annotation_document
'''
Commenting the part to add property tags in header and timeorder tag

'''


"""
function adds the information required for the annotations to work properly
"""
def add_timeorders_eaf(annotation_document):
    time_order=ET.SubElement(annotation_document,"TIME_ORDER")
    return annotation_document


"""
function forms the annotation tag
"""
def form_annotation_eaf():
    d = datetime.datetime.today()
    time = str(d.time()).split('.')[0]
    dict1 = {"AUTHOR":"",
            "DATE":str(d.date())+'T'+time+'-05:00',
            "FORMAT":"3.0",
            "VERSION":"3.0",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:noNamespaceSchemaLocation":"http://www.mpi.nl/tools/elan/EAFv3.0.xsd"
            }

    return dict1

"""
fucntion adds the default constraints that come with the eaf files
"""
def add_default_constraints_eaf(annotation_document):
    ling_dict={"1" : {"GRAPHIC_REFERENCES":"false",
                      "LINGUISTIC_TYPE_ID":"default-lt",
                      "TIME_ALIGNABLE":"true"},
                "2" : {"GRAPHIC_REFERENCES":"false",
                      "LINGUISTIC_TYPE_ID":"imported_sep",
                      "TIME_ALIGNABLE":"true"}
               }
    for key,value in ling_dict.items():
        ling_ty = ET.SubElement(annotation_document,"LINGUISTIC_TYPE")
        for item_key, item_value in value.items():
            ling_ty.set(item_key, item_value);

    constraints = [["Time subdivision of parent annotation's time interval, no time gaps allowed within this interval",
                   "Time_Subdivision"],
                ["Symbolic subdivision of a parent annotation. Annotations refering to the same parent are ordered",
                 "Symbolic_Subdivision"],
                ["1-1 association with a parent annotation",
                 "Symbolic_Association"],
                ["Time alignable annotations within the parent annotation's time interval, gaps are allowed",
                 "Included_In"]]
    for i in range(len(constraints)):
        temp_const = ET.SubElement(annotation_document,"CONSTRAINT")
        temp_const.set("DESCRIPTION", constraints[i][0])
        temp_const.set("STEREOTYPE", constraints[i][1])

    return annotation_document

def create_eaf(eaf_name):
    annotation_document = ET.Element('ANNOTATION_DOCUMENT',form_annotation_eaf())
    for key,value in form_annotation_eaf().items():
        annotation_document.set(key,value)
    
    eaf_name = os.path.splitext(eaf_name)[0]
    annotation_document = form_header(annotation_document, eaf_name)
    
    
    ### Commenting the part to add linguistic constraints after header tag in eaf file ###
#    annotation_document = add_default_constraints_eaf(annotation_document)
    
    tree = ET.ElementTree(annotation_document)
    f = BytesIO()
    tree.write(f, encoding="UTF-8", xml_declaration = True)
    
    eaf_name = eaf_name + ".eaf"
#    print (eaf_name)
    with open(eaf_name, "wb") as f1:
        f1.write(str.encode(minidom.parseString(f.getvalue()).toprettyxml(indent="   ")))
        
    f1.close()

'''
-------------------------------------------------------
END OF FUNCTIONS FOR CREATING TSCONF FILE 
-------------------------------------------------------
'''

################################################################################################################################

'''
-------------------------------------------------------
START OF FUNCTIONS FOR CREATING TSCONF FILE 
-------------------------------------------------------
'''
sentiment_dict = {
                "audio_analysis": ["Audio Sentiment",
                                   "1.0",
                                   "1.3731778E-9",
                                   "0,255,0"],
                "video_analysis": ["Video Sentiment",
                                   "1.0",
                                   "0.0",
                                   "255,0,0"],
                "text_analysis": ["Text Sentiment",
                                    "100.0",
                                   "0.0",
                                   "0,0,255"]
                    }
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
def form_tracksource(time_series, tsconf_name):
    analysis_files = [file for item in read_config(tsconf_name)[4:5] for file in item]
    indx = 0
    
    analysis_type = {}
    for item in analysis_files:
        file_type = os.path.splitext(item.split('/')[-1])[0]
        if "text_analysis" in file_type:
            analysis_type["text_analysis"] = item
        elif "audio_analysis" in file_type:
            analysis_type["audio_analysis"] = item
        elif "video_analysis" in file_type:
            analysis_type["video_analysis"] = item
    
    for key, value in sentiment_dict.items():
        tracksource_tag = ET.SubElement(time_series,"tracksource")
        tracksource_tag.set("sample-type","Discontinuous Rate")
        tracksource_tag.set("source-url",  "file:///" + analysis_type[key])
        indx += 1
        
        tracksource_tag.set("time-column", "0")
        
#        property_tag = ET.SubElement(tracksource_tag, "property")
#        property_tag.set("key", "provider")
#        property_tag.set("value", "mpi.eudico.client.annotator.timeseries.csv.CSVServiceProvider")
        
        track_tag = ET.SubElement(tracksource_tag, "track")
        track_tag.set("derivative", "0")
        track_tag.set("name", value[0])
        
        track_property_tag = ET.SubElement(track_tag, "property")
        track_property_tag.set("key", "detect-range")
        
#        if key == "text_analysis":
#            track_property_tag.set("value", "false");
#        else:
#            track_property_tag.set("value", "true");
        
        track_property_tag.set("value", "false");
        
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

def create_tsconf(tsconf_name):
    time_series = ET.Element('timeseries',form_annotation())
    for key,value in form_annotation().items():
        time_series.set(key,value)
    
    tsconf_name = os.path.splitext(tsconf_name)[0]
    time_series = form_tracksource(time_series, tsconf_name)
    
    tree = ET.ElementTree(time_series)
    f = BytesIO()
    tree.write(f, encoding="UTF-8", xml_declaration = True)
    
    tsconf_name = tsconf_name + "_tsconf.xml"
#    print (tsconf_name.split("/")[-1])
    with open(tsconf_name, "wb") as f1:
        f1.write(str.encode(minidom.parseString(f.getvalue()).toprettyxml(indent="   ")))
    
    f1.close()

'''
-------------------------------------------------------
END OF FUNCTIONS FOR CREATING TSCONF FILE 
-------------------------------------------------------
'''
################################################################################################################################

'''
-------------------------------------------------------
START OF FUNCTIONS FOR CREATING PFSX FILE 
-------------------------------------------------------
'''
def form_preferences():
    dict1 = {"version": "1.1",
             "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
             "xsi:noNamespaceSchemaLocation": "http://www.mpi.nl/tools/elan/Prefs_v1.1.xsd"
            }
    return dict1

def create_pfsx(pfsx_name):
    pref = ET.Element('preferences', form_preferences())
    for key, value in form_preferences().items():
        pref.set(key, value)

    pref1_tag = ET.SubElement(pref, "pref")
    pref1_tag.set("key", "TimeSeriesViewer.NumberOfPanels")
    int1_tag = ET.SubElement(pref1_tag, "Int")
    int1_tag.text = "2"
    
    prefList1_tag = ET.SubElement(pref, "prefList")
    prefList1_tag.set("key", "TimeSeriesViewer.Panel-1")
    string_subtag_audio = ET.SubElement(prefList1_tag, "String")
    string_subtag_audio.text = "Audio Sentiment"
    string_subtag_video = ET.SubElement(prefList1_tag, "String")
    string_subtag_video.text = "Video Sentiment"
    prefList2_tag = ET.SubElement(pref, "prefList")
    prefList2_tag.set("key", "TimeSeriesViewer.Panel-2")
    string_subtag_text = ET.SubElement(prefList2_tag, "String")
    string_subtag_text.text = "Text Sentiment"
    
    tree = ET.ElementTree(pref)
    f = BytesIO()
    tree.write(f, encoding="UTF-8", xml_declaration = True)
    pfsx_name = os.path.splitext(pfsx_name)[0] + ".pfsx"
    with open(pfsx_name, "wb") as f1:
        f1.write(str.encode(minidom.parseString(f.getvalue()).toprettyxml(indent="   ")))
    
    f1.close()

'''
-------------------------------------------------------
END OF FUNCTIONS FOR CREATING PFSX FILE 
-------------------------------------------------------
'''

def generate_elan_files(config_file_path):
    create_eaf(config_file_path)
    create_tsconf(config_file_path)
    create_pfsx(config_file_path)
   
def main():
    session_names = os.listdir(session_path)
    for session_id in session_names:
        try:
            media_path = session_path + session_id + "/session_data/subject_media/processedVideos/"
            media_session_intervals= os.listdir(media_path)
            
            analysis_path = session_path + session_id + "/analysis_data/"
            analysis_session_intervals = os.listdir(analysis_path)
            print (session_id)
            
            for file_num in range(len(analysis_session_intervals)):
                curr_config_file_path = session_path + session_id + "/" + analysis_session_intervals[file_num] + ".txt"
                config_file = open(curr_config_file_path, "w")
                config_file.write("vid_file | " + "session_data/subject_media/processedVideos/" + media_session_intervals[file_num])
                config_file.write("\n")
                config_file.write("audio_analysis | " + "analysis_data/" + analysis_session_intervals[file_num] + "/audio_analysis_subject.txt")
                config_file.write("\n")
                config_file.write("video_analysis | " + "analysis_data/" + analysis_session_intervals[file_num] + "/video_analysis_subject.txt")
                config_file.write("\n")
                config_file.write("text_analysis | " + "analysis_data/" + analysis_session_intervals[file_num] + "/text_analysis_subject.txt")
                config_file.close()
                
                generate_elan_files(curr_config_file_path)
                print ("EAF, TSCONF.XML and PFSX files generated successfully.\n\n")        
        except:
            pass
            

if __name__ == "__main__":
    main()
        
        