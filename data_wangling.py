# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 18:56:38 2015

@author: karthik
"""

import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def update_postal(postcode):
    if postcode.isdigit():
        return postcode
    elif re.findall("\.",postcode):
        return postcode.replace(" ","").replace(".","")
#        no_dot=re.sub("\.","",postcode).replace(" ","")
#        return (no_dot)
    else:   
        return postcode.replace(" ","")
#        no_space=postcode.replace(" ","")
#        return no_space

    
def update_street(street_name):
    street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
    expected = ["Street", "Avenue", "Road",'koyambedu','Nagar','Salai']
    mapping = { 'Ave': "Avenue",
               'NAGAR':'Nagar',
               "St": "Street",
               'ROAD':"Road",
               "Rd":"Road",
               'Road)':"Road",
               'Road,kodambakkam':"Road",
               'Street,':"Street",
               'Strret':"Street",
               'nagar':'Nagar',
               'road': "Road",
               'street':"Street" 
               }
    Street_type=re.search(street_type_re,street_name)
    
    if Street_type:
        r=Street_type.group()
        if r  in mapping.keys():
            update_street_name=re.sub(street_type_re,mapping[Street_type.group()],street_name)
            
        else:
            update_street_name=street_name
        return update_street_name
    
    
    
def shape_element(element):
    ref=[]
    address={}
    node = {}
    a=[0,0]
    
    CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
    if element.tag=="node" or element.tag == "way" :
        data=element.attrib
        node["created"]={i:data[i] for i in CREATED}
        for key,value in data.items():
                if key=="lat":
                    lat=float(data[key])
                    a[0]=lat
                elif key=="lon":
                    lon=float(data[key])
                    a[1]=lon
                elif key not in CREATED:
                    node[key]=data[key]
        node["type"]=element.tag
        node["pos"]=a
        
        for child in element:
            if child.tag=="tag" or child.tag=="nd" :
                sub_tab=child.attrib
                for key, value in sub_tab.items():
                    if key=='k':
                        
                        if re.search(problemchars,value):
                            continue
#                        if re.findall("post",value):
#                            address["postal_code"]=update_postal(child.attrib["v"])
                        if re.search(lower_colon,value):
                            if value=='addr:street':
                                address["street"]=update_street(child.attrib['v'])
                            else:
                                try:
                                    m=re.search("(?<=addr:)\w+",value)
                                    k=m.group(0)
                                    address[k]=sub_tab['v']
                                except :
                                    pass
                        if re.search(lower,value):
                            node[value]=sub_tab['v']
                        node["address"]=address
                    elif key=="ref":
                         ref.append(value)
        if ref:
            node["node_refs"]=ref
        try:
            if node["address"]=={}:
                del node["address"]
        except:
            pass
        return node 
    else:
        return None
    
def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w",encoding="utf8") as fo:
        for event, element in ET.iterparse(file_in):
            el = shape_element(element)
            
            if el:
                data.append(el)
                #print (data)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data
    
    
file=r"C:\Users\karthik\Desktop\udacity\p3\project\chennai.osm" 
data=process_map(file,True)
