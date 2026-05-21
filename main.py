#! python

# main.py

# import necessary libraries
import sys
import os
import re
from dotenv import load_dotenv
import requests
import xml.etree.ElementTree as ET
import pandas as pd
sys.path.append("utils")
from utils import get_ncbi_api_key
from query_pubmed import query_pubmed
from query_crossref import query_crossref
from synapse import get_all_pubs

# find new pubs, update pub metadata
# write to csv for human-in-the-loop review and PR merge
def main():
  ncbiapikey = get_ncbi_api_key()
  
  all_ark_pubs = get_all_pubs() # returns dict of PMID and DOI lists for stuff already tracked in backend
  
  # perform broad query in pubmed for AMP publications
  results = {}
  results['pubmed'] = query_pubmed(tracked_pubs = all_ark_pubs, token = ncbiapikey)
  
  doi = [x for x in all_ark_pubs["DOI"] if x not in list(results['pubmed']['DOI'])]
  # query CrossRef for pub metadata by doi for pubs not yet in pubmed
  results['crossref'] = query_crossref(doi)
  
  results = pd.concat([results['pubmed'], results['crossref']])
  
  new_pubs = results[results['DOI'].isin(doi) == False] # pubs with a DOI that we don't have tracked
  fid = "new_publications.csv"
  new_pubs.to_csv(fid, index = False)
  
  pub_updates = results[results['DOI'].isin(doi) == True] # pubs with a DOI that we DO have tracked but don't yet have a PMID
  fid = "publication_updates.csv"
  pub_updates.to_csv(fid, index = False)

if __name__ == "__main__":
  # calling main function
  main()

