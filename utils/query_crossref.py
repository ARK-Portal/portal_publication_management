#! python

# query_crossref.py

'''
A set of functions to queries CrossRef API using DOI and pull key publication 
metadata that will be used for filtering, categorizing, and annotating 
publications that are found
'''

# import necessary functions
import sys
import requests
import json
import pandas as pd
from utils import *

def query_crossref(doi):
  with open('json/metadata_translation.json', 'r') as file:
    out = json.load(file)['crossref']

  for d in doi:
    #print(d)
    query = ["https://api.crossref.org/works/doi/", d]
    query = ''.join(query)
    query_response = requests.get(query)
    results = json.loads(query_response.content)['message']
    journal_dict = get_journal(results)
    
    pubDate = results['published']['date-parts'][0]
    out['year'].append(pubDate[0])
    
    out['journal'].append(journal_dict['journal'])
    out['title'].append(results['title'][0])
    
    pubDate = [str(x) for x in pubDate]
    pubDate = '-'.join(pubDate)
    out['publicationDate'].append(pubDate)
    
    authors = process_cr_authors(authors = results['author'])
    out['authors'].append(authors)
    out['name'] = " ".join([results['author'][0]['family'], journal_dict['journal_short'], "TBD"])
  
  out = pd.DataFrame(out)
  out['DOI'] = doi
  # add additional columns to fill out annotation template
  out = finalize_pub_metadata(out)
  
  return(out)

def process_cr_authors(authors):
  out = []
  for author in authors:
    if 'name' in author.keys():
      out.append(author['name'])
    else:
      name = ' '.join([author['given'], author['family']])
      out.append(name)
  
  out = ", ".join(out)
  return(out)

def get_journal(results):
  translate = {'bioRxiv': 'Biorxiv : The Preprint Server For Biology', 
               'medRxiv': 'Medrxiv : The Preprint Server For Health Sciences'}
  
  if 'institution' in results.keys():
    journal_short = results['institution'][0]['name']
    journal = translate[journal_short]
  else:
    journal_short = results['short-container-title'][0]
    journal = results['container-title'][0]
  
  out = {'journal': journal, 'journal_short': journal_short}
  return(out)




# END
