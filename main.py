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
from utils import get_ncbi_api_key, harmonize_pub_df
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
  print(f"Pubmed query complete! {results['pubmed'].shape[0]} results found.")
  
  doi = [x for x in all_ark_pubs["DOI"] if x not in list(results['pubmed']['DOI'])]
  if len(doi) > 0:
    # query CrossRef for pub metadata by doi for pubs not yet in pubmed
    results['crossref'] = query_crossref(doi)
    print(f"CrossRef query complete! {results['crossref'].shape[0]} results found.")
    results = pd.concat([results['pubmed'], results['crossref']])
  else:
    results = results['pubmed']
  
  new_pubs = results[results['DOI'].isin(doi) == False] # pubs with a DOI that we don't have tracked
  if new_pubs.shape[0] > 0:
    print(f"{new_pubs.shape[0]} new publications found.")
    fid = "new_publications.csv"
    new_pubs.to_csv(fid, index = False)
  
  pub_updates = results[results['DOI'].isin(doi) == True] # pubs with a DOI that we DO have tracked but don't yet have a PMID
  if pub_updates.shape[0] > 0:
    print(f"{pub_updates.shape[0]} publications updates.")
    
    df = all_ark_pubs['data']
    df = df.loc[:, ['DOI', 'id', 'associatedDataset']]
    pub_updates = pub_updates.drop(columns = ['associatedDataset'])
    pub_updates = pd.merge(pub_updates, df, on = 'DOI', how = 'left')
    pub_updates = harmonize_pub_df(pub_updates, add = ['id'])
    
    fid = "publication_updates.csv"
    pub_updates.to_csv(fid, index = False)
  
  df = all_ark_pubs['data']
  TBD_pubs = df[df['name'].str.contains("TBD") == True]
  TBD_pubs = harmonize_pub_df(TBD_pubs, add = ['id'])
  if TBD_pubs.shape[0] > 0:
    print(f"{TBD_pubs.shape[0]} TBD publications are tracked in backend project already.")
    fid = "TBD_publications.csv"
    TBD_pubs.to_csv(fid, index = False)

if __name__ == "__main__":
  # calling main function
  main()

