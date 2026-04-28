#! python

# query_pubmed.py

'''
A set of functions to pubmed for Accelerating Medicines Partnership publications
'''

# import necessary libraries
import sys
import requests
import xml.etree.ElementTree as ET
import pandas as pd

def query_pubmed_ids(ignore_ids):
  query = ["https://eutils.ncbi.nlm.nih.gov/", 
           "entrez/eutils/esearch.fcgi?db=pubmed",
           "&api_key=", ncbiapikey,
           "&retmax=1000",
           "&term=Accelerating+Medicines+Partnership+AND+", 
           "2025", "[pdat]"]
  query = ''.join(query)
  
  query_response = requests.get(query)
  root = ET.fromstring(query_response.content)
  pubmed_ids = []
  for child in root.findall('./IdList/Id'):
    pubmed_ids.append(child.text)
  pubmed_ids = list(set(pubmed_ids))
  
  # remove pubmed ids already cataloged in ARK portal
  pubmed_ids = [x for x pubmed_ids if x not in ignore_ids]
  
  return(pubmed_ids)

def pmid_to_doi(ids):
  uid_list = ",".join(ids)
  #esummary.fcgi?db=<database>&id=<uid_list>
  query = ["https://eutils.ncbi.nlm.nih.gov/", 
           "entrez/eutils/esummary.fcgi?db=pubmed",
           "&api_key=", ncbiapikey,
           "&id=", uid_list]
  query = ''.join(query)
  query_response = requests.get(query)
  root = ET.fromstring(query_response.content)
  
  data = {}
  for child in root:
    id = child.find('Id').text
    data[id] = {}
    for gchild in child.iter('Item'):
      #name = gchild.find('name').text
      name = gchild.get('Name')
      #print(id, gchild.text, name)
      data[id][name] = gchild.text
  
  doi = []
  for id in data:
    if 'doi' in data[id].keys():
      doi.append(data[id]['doi'])
    else:
      doi.append(None)
    
  return(doi)


# END
