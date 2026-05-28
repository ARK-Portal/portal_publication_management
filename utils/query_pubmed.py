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
import urllib.parse
from utils import *

def get_xmlroot_to_pmid(root):
  pubmed_ids = []
  for child in root.findall('./IdList/Id'):
    pubmed_ids.append(child.text)
  
  pubmed_ids = list(set(pubmed_ids))
  return(pubmed_ids)

def perform_scoped_query(token):
  with open('json/scope_query.json', 'r') as file:
    scoped_queries = json.load(file)
  
  url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
  
  results = []
  today = datetime.now()
  for scope in scoped_queries.keys():
    # finish defining query key-value pairs
    term = scoped_queries[scope]['term']
    term = "".join([term, str(today.year), '[pdat]'])
    #term = "".join([term, '2025', '[pdat]'])
    scoped_queries[scope]['term'] = term
    
    scoped_queries[scope]['api_key'] = token
    
    query = url + urllib.parse.urlencode(scoped_queries[scope])
    query_response = requests.get(query)
    root = ET.fromstring(query_response.content)
    pubmed_ids = get_xmlroot_to_pmid(root)
    results.append(get_pubmed_metadata(ids = pubmed_ids, token = token, scope = scope))
  
  results = pd.concat(results)
  results = results.drop_duplicates()
  
  return(results)


def query_pubmed(tracked_pubs, token):
  
  pub_meta = perform_scoped_query(token)
  # remove pubmed ids already cataloged in ARK portal
  pub_meta = pub_meta[pub_meta['PMID'].isin(tracked_pubs['PMID']) ==False]
  #pubmed_ids = [x for x in pubmed_ids if x not in tracked_pubs['PMID']]
  
  # search pubmed for doi not yet with a pmid in synapse
  # if a pub gets filtered out by scoped filtering it will still be captured if we have the doi tracked
  doi = [d for d in tracked_pubs['DOI'] if d not in pub_meta['DOI']]
  url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
  doi2pmid = []
  for d in doi:
    q = {"db": "pubmed", "retmax": 1, 'api_key': token, "term": d}
    query = url + urllib.parse.urlencode(q)
    query_response = requests.get(query)
    root = ET.fromstring(query_response.content)
    doi2pmid = doi2pmid + get_xmlroot_to_pmid(root)
  
  if len(doi2pmid) > 0:
    more_pub_meta = get_pubmed_metadata(ids = doi2pmid, token = token, scope = None)
    pub_meta = pd.concat([pub_meta, more_pub_meta])
  
  return(pub_meta)

def get_pubmed_metadata(ids, token, scope = None):
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
    metadata_translation = json.load(file)['pubmed']
  
  results = {'Source': [], 'authors': [], 'FirstAuthorSurname': []}
  for k in metadata_translation.keys():
    results[k] = []
  
  for id in data:
    for k in results.keys():
      if k in data[id].keys():
        #print(f"{k} found, adding {data[id][k]} to results.")
        results[k].append(data[id][k])
      else:
        #results[k].append('Not Available')
        results[k].append('')
  
  results = pd.DataFrame(results)
  results['PMID'] = list(data.keys())
  if scope is not None:
    # select for AMP AIM and AMP RA/SLE publications
    with open('json/scope_filters.json', 'r') as file:
      program_filter = json.load(file)
    
    test = '|'.join(program_filter[scope])
    results = results[results['authors'].str.contains(test)]
    results = results.reset_index(drop = True)
  
  results = process_pubmed_results(results, trans = metadata_translation)
  
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
  
  # modify identifiers for synapse registry match
  idx = [i for i, x in enumerate(results['PMID']) if x == '']
  results['PMID'] = [''.join(['PMID:', x]) for x in results['PMID']]
  results.loc[idx, 'PMID'] = None
  
  idx = [i for i, x in enumerate(results['PMCID']) if x == '']
  results['PMCID'] = [''.join(['pmc:', x]) for x in results['PMCID']]
  results.loc[idx, 'PMCID'] = None
  
  # add additional columns to fill out annotation template
  results = finalize_pub_metadata(results)
  
  return(results)




# END
