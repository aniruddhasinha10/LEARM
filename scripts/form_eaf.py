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
    config_file = "../Sessions/IM175_1/IM175_1_part-1_video_Nov_25_2019_18.10.00_18.28.31.txt"
    configs = []
    with open(config_file,'r') as config:
        configs = config.read().split('\n')
    
    media_file_names = []
    media_file_formats = []
    rel_media_paths=[]

    session_id = config_file.split("/")[2]
    for config in configs:
        if any(c.isalpha() for c in config):
            if "vid_file" in config[:8]:
                splits = config.split(' | ')
                temp = splits[1]
    
                link_url = temp
                media_file_names.append(link_url)
                rel_url = "../../" + session_id + "/" + link_url
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
                rel_analysis_paths.append('../' + session_id + "/" + analysis_path)

    return [media_file_names,media_file_formats,
            rel_media_paths,analysis_names,
            analysis_files, rel_analysis_paths]



"""
fucntion adds the tags for specifying media files
"""
def add_media(header_tag,files):
    print(files)
    for i in range(len(files[0])):
        print("done")
        media_descriptor = ET.SubElement(header_tag,"MEDIA_DESCRIPTOR")
        media_descriptor.set("MEDIA_URL",files[0][i])
        media_descriptor.set("MIME_TYPE",files[1][i])
        media_descriptor.set("RELATIVE_MEDIA_URL",files[2][i])
    return header_tag

"""
fucntion adds the tags for specifying linked analysis files
"""
def add_linked_file(header_tag,files):
    for i in range(len(files[0])):
        linked_file_descriptor = ET.SubElement(header_tag,"LINKED_FILE_DESCRIPTOR")
        linked_file_descriptor.set("LINK_URL",files[1][i])
        linked_file_descriptor.set("MIME_TYPE","text/plain")
        linked_file_descriptor.set("RELATIVE_LINK_URL",files[2][i])
    
    linked_file_descriptor = ET.SubElement(header_tag,"LINKED_FILE_DESCRIPTOR")
    tsconf_file_name = "IM175_1_part-1_video_Nov_25_2019_18.10.00_18.28.31_tsconf.xml"
    linked_file_descriptor.set("LINK_URL", tsconf_file_name)
    linked_file_descriptor.set("MIME_TYPE","text/xml")
    linked_file_descriptor.set("RELATIVE_LINK_URL", "./" + tsconf_file_name)
    
    return header_tag


"""
function forms the header section in final eaf file
"""
def form_header(annotation_document):
    header_tag = ET.SubElement(annotation_document,"HEADER")
    header_tag.set("MEDIA_FILE","")
    header_tag.set("TIME_UNITS","milliseconds")
    header_tag = add_media(header_tag,read_config()[:3])
    header_tag = add_linked_file(header_tag, read_config()[3:])
    property_1 = ET.SubElement(header_tag,"PROPERTY")
    property_1.set("NAME","URN")
    property_1.text = "urn:nl-mpi-tools-elan-eaf:298594aa-e982-4e4a-aae2-fa40fca12994"
    property_2 = ET.SubElement(header_tag,"PROPERTY")
    property_2.set("NAME","lastUsedAnnotationId")
    property_2.text = "1813"
    annotation_document = add_annotations_eaf(annotation_document)
    return annotation_document

"""
function adds the information required for the annotations to work properly
"""
def add_annotations_eaf(annotation_document):
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

def main():
    annotation_document = ET.Element('ANNOTATION_DOCUMENT',form_annotation_eaf())
    for key,value in form_annotation_eaf().items():
        annotation_document.set(key,value)
    
    annotation_document = form_header(annotation_document)
    annotation_document = add_default_constraints_eaf(annotation_document)
    res = read_config()
    tree = ET.ElementTree(annotation_document)
    f = BytesIO()
    tree.write(f, encoding="UTF-8", xml_declaration = True)
    
    eaf_name = "../Sessions/IM175_1/IM175_1_part-1_video_Nov_25_2019_18.10.00_18.28.31.eaf"
    with open(eaf_name, "wb") as f1:
        f1.write(str.encode(minidom.parseString(f.getvalue()).toprettyxml(indent="   ")))


if __name__ == "__main__":
    main()
