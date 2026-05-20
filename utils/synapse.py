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
  df = query("SELECT id, DOI, PMID from syn64429484")
  
  out = {'PMID': [], 'DOI': []}
  pmid = df[df.PMID.str.match("^PMID:") == True]
  out['PMID'] = list(set(list(pmid.PMID)))
  out['PMID'] = [item.replace("PMID:", "") for item in out['PMID']]
  doi = df[df.DOI.str.match("^10") == True]
  out['DOI'] = list(set(list(doi.DOI)))
  
  return(out)

# END
  
