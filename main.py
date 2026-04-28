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
from utils import *
from query_pubmed import *
from synapse import *

# find new pubs, update pub metadata
# write to csv for human-in-the-loop review and PR merge
def main():
  
  ncbiapikey = get_ncbi_api_key()
  
  all_ark_pubs = get_all_pubs() # returns dict of PMID and DOI lists
  
  pubmed_ids = query_pubmed_ids(ignore_ids = all_ark_pubs['PMID'])
  doi = pmid_to_doi(ids = pubmed_ids)
  
  results = pd.DataFrame({'PMID': pubmed_ids, 'DOI': doi})
  results = results.dropna()
  
  results = query_crossref(results)
  results = filter_results(results)

if __name__ == "__main__":
  # calling main function
  main()

