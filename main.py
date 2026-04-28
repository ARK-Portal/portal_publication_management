#! python

# main.py

# import necessary libraries
import sys
import os
from dotenv import load_dotenv
import requests
import xml.etree.ElementTree as ET
import pandas as pd

def main():
  
  ark_catalog = get_ark_pubs()
  
  ncbiapikey = get_ncbi_api_key()
  
  pubmed_ids = query_pubmed_ids(ignore_ids = list(ark_catalog['PMID']))
  doi = pmid_to_doi(ids = pubmed_ids)
  
  results = pd.DataFrame({'PMID': pubmed_ids, 'DOI': doi})
  results = results.dropna()
  
  results = query_crossref(results)
  results = filter_results(results)

if __name__ == "__main__":
  # calling main function
  main()

