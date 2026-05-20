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

def query_crossref(doi):
  with open('json/metadata_translation.json', 'r') as file:
    out = json.load(file)['crossref']

  for d in doi:
    query = ["https://api.crossref.org/works/doi/", d]
    query = ''.join(query)
    query_response = requests.get(query)
    results = json.loads(query_response.content)['message']
    
    pubDate = results['posted']['date-parts'][0]
    journal = results['institution'][0]['name']
    out['journal'].append(journal)
    out['year'].append(pubDate[0])
    out['title'].append(results['title'][0])
    
    pubDate = [str(x) for x in pubDate]
    pubDate = '-'.join(pubDate)
    out['publicationDate'].append(pubDate)
    
    authors = process_cr_authors(authors = results['author'])
    out['authors'].append(authors)
    out['name'] = " ".join([results['author'][0]['family'], journal, "TBD"])

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






# END
