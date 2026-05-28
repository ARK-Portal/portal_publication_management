#! python

# synapse.py

'''
A set of functions involving Synapse Client actions
'''

# import necessary functions
import sys
import synapseclient
import pandas as pd
import synapseutils
from synapseclient.models import query, File, Table

def get_all_pubs():
  '''
  returns dict of PMID and DOI lists for stuff already tracked in backend 
  entity view 'All Publications'
  '''
  syn = synapseclient.login()
  df = query("SELECT * from syn64429484")
  
  out = {'PMID': [], 'DOI': [], 'data': df}
  pmid = df[df.PMID.str.match("^PMID:") == True]
  out['PMID'] = list(set(list(pmid.PMID)))
  #out['PMID'] = [item.replace("PMID:", "") for item in out['PMID']]
  
  # only return DOI for pubs without a PMID 
  # this way we query CrossRef for pubs not yet in pubmed
  doi = df[df.PMID.str.match("^PMID:") != True] # remove pubs with PMID
  doi = doi[doi.DOI.str.match("^10") == True] # then select those with DOI
  out['DOI'] = list(set(list(doi.DOI)))
  
  return(out)

# END
  
