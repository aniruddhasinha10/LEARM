# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 10:48:54 2019

@author: Karthik Vikram
"""
from io import BytesIO
from lxml import etree
from xml.dom import minidom
import datetime
import xml.etree.ElementTree as ET
import pandas as pd

"""
function that converts time in string to milliseconds
"""
def convert_to_milliseconds(time):
    total_time=0
    step=60000
    ch_l=list(time.split('.')[-4] + time.split('.')[-3])
    total_time = total_time + int(ch_l[3])*step
    total_time = total_time + int(ch_l[2])*step*10
    total_time = total_time + int(ch_l[1])*step*60
    total_time = total_time + int(ch_l[0])*step*600
    total_time += int(time.split('.')[-1]) + int(time.split('.')[-2])*1000
    return str(total_time)

"""
function reads data from a standard CSV file
"""
def read_csv(csv_file_name):
    data=pd.read_csv(csv_file_name)
    return data.loc[:,['start','end','value']].values.tolist()

"""
function reads config data from config.txt file
"""
def read_config():
    configs = []
    with open('./config.txt','r') as config:
        configs=config.read().split('\n')
    file_names = []
    file_formats = []
    rel_paths=[]
    
    for config in configs:
        if any(c.isalpha() for c in config):
            if "aud_file" in config[:8] or "vid_file" in config[:8]:
                temp=config.split(' | ')[1]
                
                temp="file:///"+temp
                file_names.append(temp)
                rel_path="./"+temp.split('/')[-1]+"/"
                rel_paths.append(rel_path)
                if ".wav" in temp.split('/')[-1]:
                    file_formats.append("audio/x-wav")
                if ".mp4" in temp.split('/')[-1]:
                    file_formats.append("video/mp4")
                    
    analysis_names = []
    analysis_files = []
    for config in configs:
        if any(c.isalpha() for c in config):
            if "analysis" in config:
                analysis_names.append(config.split(' | ')[0].strip())
                analysis_files.append(config.split(' | ')[1].strip())
    
    return [file_names,file_formats,rel_paths,analysis_names,analysis_files]

"""
function forms the annotation tag
"""
def form_annotation():
    d = datetime.datetime.today()
    time=str(d.time()).split('.')[0]
    
    dict1 = {"AUTHOR":"LEARM",
            "DATE":str(d.date())+'T'+time+'-05:00',
            "FORMAT":"3.0",
            "VERSION":"3.0"
            }
    
    return dict1

"""
fucntion adds the tags for specifying media files
"""
def add_media(header_tag,files):
    for i in range(len(files[0])):
        media_descriptor = ET.SubElement(header_tag,"MEDIA_DESCRIPTOR")
        media_descriptor.set("MEDIA_URL",files[0][i])
        media_descriptor.set("MIME_TYPE",files[1][i])
        media_descriptor.set("RELATIVE_MEDIA_URL",files[2][i])
    return header_tag

"""
function matches the annotations to their time slots
"""
def add_tier_info(annotation_document,tier_name,values,prev_count):
    tier=ET.SubElement(annotation_document,"TIER")
    tier.set("DEFAULT_LOCALE","en")
    tier.set("LINGUISTIC_TYPE_REF","default-lt")
    tier.set("TIER_ID",tier_name)
    count=prev_count
    for i in range(len(values)):
        annotation=ET.SubElement(tier,"ANNOTATION")
        align_ann=ET.SubElement(annotation,"ALIGNABLE_ANNOTATION")
        align_ann.set("ANNOTATION_ID",("a"+str(len(values)+i)))
        align_ann.set("TIME_SLOT_REF1",("ts"+str(count)))
        count+=1
        align_ann.set("TIME_SLOT_REF2",("ts"+str(count)))
        count+=1
        ET.SubElement(align_ann,"ANNOTATION_VALUE").text=str(values[i][2])
    return annotation_document,count 

"""
function adds the information required for the annotations to work properly
"""
def add_annotations(annotation_document):
    time_order=ET.SubElement(annotation_document,"TIME_ORDER")
    analysis=read_config()[3:]
    values=[]
    for csv_file in analysis[1]:
        values+=read_csv(csv_file)
    count=1
    for i in range(len(values)):
            time_slot=ET.SubElement(time_order,"TIME_SLOT")
            time_slot.set("TIME_SLOT_ID",("ts"+str(count)))
            time_slot.set("TIME_VALUE",convert_to_milliseconds(values[i][0]))
            count=count+1
            time_slot=ET.SubElement(time_order,"TIME_SLOT")
            time_slot.set("TIME_SLOT_ID",("ts"+str(count)))
            time_slot.set("TIME_VALUE",convert_to_milliseconds(values[i][1]))
            count=count+1
    count_seed=1
    for i in range(len(analysis[0])):
        annotation_document,count_seed=add_tier_info(annotation_document,analysis[0][i],read_csv(analysis[1][i]),count_seed)
    return annotation_document
    
"""
function forms the header section in final eaf file
"""
def form_header(annotation_document):
    header_tag = ET.SubElement(annotation_document,"HEADER")
    header_tag.set("MEDIA_FILE","")
    header_tag.set("TIME_UNITS","milliseconds")
    header_tag = add_media(header_tag,read_config()[:3])
    property_1 = ET.SubElement(header_tag,"PROPERTY")
    property_1.set("NAME","URN")
    property_1.text = "urn:nl-mpi-tools-elan-eaf:298594aa-e982-4e4a-aae2-fa40fca12994"
    property_2 = ET.SubElement(header_tag,"PROPERTY")
    property_2.set("NAME","lastUsedAnnotationId")
    property_2.text = "0"
    annotation_document = add_annotations(annotation_document)
    return annotation_document

"""
fucntion adds the default constraints that come with the eaf files
"""
def add_default_constraints(annotation_document):
    ling_ty=ET.SubElement(annotation_document,"LINGUISTIC_TYPE")
    ling_dict={"GRAPHIC_REFERENCES":"false",
               "LINGUISTIC_TYPE_ID":"default-lt","TIME_ALIGNABLE":"true"}
    for key,value in ling_dict.items():
        ling_ty.set(key,value)
    constraints = ["Time subdivision of parent annotation's time interval, no time gaps allowed within this interval","Time_Subdivision","Symbolic subdivision of a parent annotation. Annotations refering to the same parent are ordered","Symbolic_Subdivision",
"1-1 association with a parent annotation","Symbolic_Association","Time alignable annotations within the parent annotation's time interval, gaps are allowed","Included_In"]
    for i in range(0,len(constraints),2):
        temp_const=ET.SubElement(annotation_document,"CONSTRAINT")
        temp_const.set("DESCRIPTION",constraints[i])
        temp_const.set("STEREOTYPE",constraints[i+1])
        
    return annotation_document

def main():
    annotation_document = ET.Element('ANNOTATION_DOCUMENT',form_annotation())
    for key,value in form_annotation().items():
        annotation_document.set(key,value)
    
    annotation_document = form_header(annotation_document)
    annotation_document = add_default_constraints(annotation_document)
    
    tree = ET.ElementTree(annotation_document)
    f = BytesIO()
    tree.write(f,encoding='UTF-8', xml_declaration=True)
    
    eaf_name = "./"+read_config()[0][1].split('/')[-1].split('.')[0]+".eaf"
    with open(eaf_name, "wb") as f1:
        f1.write(str.encode(minidom.parseString(f.getvalue()).toprettyxml(indent="   ")))


if __name__ == "__main__":
    main()