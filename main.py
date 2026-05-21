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
from query_crossref import *
from synapse import *

# find new pubs, update pub metadata
# write to csv for human-in-the-loop review and PR merge
def main(scope = None):
  if scope is None:
    print("please provide a 'scope' for excuting this function")
  else:
    ncbiapikey = get_ncbi_api_key()
    
    all_ark_pubs = get_all_pubs() # returns dict of PMID and DOI lists for stuff already tracked in backend
    
    # perform broad query in pubmed for AMP publications
    pubmed_ids = query_pubmed_ids(ignore_ids = all_ark_pubs['PMID'], token = ncbiapikey)
    # using returned pubmed ids query pubmed for publication metadata
    pm_results = get_pubmed_metadata(pubmed_ids, token = ncbiapikey, scope = scope)
    
    doi = [x for x in all_ark_pubs["DOI"] if x not in list(pm_results['DOI'])]
    # query CrossRef for pub metadata for pubs not yet in pubmed
    cr_results = query_crossref(doi)
    
    results = pd.concat([pm_results, cr_results])
    
    fid = "new_publications.csv"
    pm_results.to_csv(fid, index = False)

if __name__ == "__main__":
  # calling main function
  main()

