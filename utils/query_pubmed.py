#! python

# query_pubmed.py

'''
A set of functions to pubmed for Accelerating Medicines Partnership publications
'''

# import necessary libraries
import sys
import requests
import json
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
from utils import *

def query_pubmed_ids(ignore_ids, token):
  query = ["https://eutils.ncbi.nlm.nih.gov/", 
           "entrez/eutils/esearch.fcgi?db=pubmed",
           "&api_key=", token,
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
  pubmed_ids = [x for x in pubmed_ids if x not in ignore_ids]
  
  return(pubmed_ids)

def get_pubmed_metadata(ids, token, scope):
  uid_list = ",".join(ids)
  #esummary.fcgi?db=<database>&id=<uid_list>
  query = ["https://eutils.ncbi.nlm.nih.gov/", 
           "entrez/eutils/esummary.fcgi?db=pubmed",
           "&api_key=", token,
           "&id=", uid_list]
  query = ''.join(query)
  query_response = requests.get(query)
  root = ET.fromstring(query_response.content)
  data = get_xml_grandchild(root)
  
  with open('json/metadata_translation.json', 'r') as file:
    metadata_translation = json.load(file)
  
  results = {'Source': [], 'authors': [], 'FirstAuthorSurname': []}
  for k in metadata_translation.keys():
    results[k] = []
  
  for id in data:
    for k in results.keys():
      if k in data[id].keys():
        #print(f"{k} found, adding {data[id][k]} to results.")
        results[k].append(data[id][k])
      else:
        results[k].append('Not Available')
  
  results = pd.DataFrame(results)
  results['PMID'] = list(data.keys())
  # select for AMP AIM and AMP RA/SLE publications
  with open('json/scope_filters.json', 'r') as file:
    program_filter = json.load(file)
  
  test = '|'.join(program_filter[scope])
  results = results[results['authors'].str.contains(test)]
  results = results.reset_index(drop = True)
  
  #results = process_pubmed_results(results, trans = metadata_translation)
  
  return(results)

def get_xml_grandchild(root):
  data = {}
  for child in root:
    id = child.find('Id').text
    data[id] = {}
    for gchild in child.iter('Item'):
      name = gchild.get('Name')
      if name == 'AuthorList':
        authors = []
        for ggchild in gchild.iter("Item"):
          if ggchild.text != '\n\t\t':
            authors.append(ggchild.text)
        data[id]['authors'] = ", ".join(authors)
        # get surname of first author
        first_auth = authors[0]
        #first_auth.split()[0]
        data[id]['FirstAuthorSurname'] = first_auth.split()[0]
        
      else:
        data[id][name] = gchild.text
  
  return(data)

def process_pubmed_results(results, trans):
  results['year'] = results['PubDate'].apply(lambda x: x.split()[0])
  x = ['FirstAuthorSurname', 'Source', 'year', 'PMID']
  results['name'] = results[x].apply(lambda row: " ".join([row['FirstAuthorSurname'], row['Source'], row['year'], row['PMID']]), axis = 1)
  results = results.rename(columns = trans)
  
  # add additional columns to fill out annotation template
  ## guess at program label
  results['program'] = results['authors'].apply(lambda x:guess_annotation(x, which = "program"))
  results['project'] = results['title'].apply(lambda x:guess_annotation(x, which = "project"))
  results['URL'] = [''.join(["https://doi.org/", x]) if re.search('10', x) else None for x in results['DOI']]
  ## guess at publicationType
  x = list(map(lambda x, y: '|'.join([x,y]), list(results.title), list(results.journal)))
  results['publicationType'] = list(map(lambda x, y: guess_pubType(x, y), list(results.title), list(results.journal)))
  
  # modify identifiers for synapse registry match
  results['PMID'] = [''.join(['PMID:', x]) for x in results['PMID']]
  results['PMCID'] = [''.join(['pmc:', x]) for x in results['PMCID']]
  
  anno_template = get_ark_pub_anno_template()
  keep = [x for x in list(results.columns) if x in list(anno_template.columns)]
  results = results.loc[:, keep]
  add = [x for x in list(anno_template.columns) if x not in list(results.columns)]
  
  return(results)


# END
