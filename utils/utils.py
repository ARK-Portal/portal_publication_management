#! python

# utils.py

'''
general utility funcitons to support workflow execution
'''

import os
from dotenv import load_dotenv
import re

def get_ncbi_api_key():
  # Load local .env file (if it exists)
  load_dotenv()
  
  # Access variables (works locally and in GitHub Actions)
  ncbiapikey = os.getenv("NCBI_API_KEY")
  
  if not ncbiapikey:
    raise Exception("NCBI_API_KEY not found!")
  else:
    return(ncbiapikey)

def guess_program(x):
  match_strings = {"AMP RA/SLE": "AMP RA/SLE|lupus|rheumatoid", 
                   "AMP AIM": "AMP AIM|autoimmune"}
  out = []
  for x in match_strings.keys():
    match = re.search(match_strings[x], x, flags=re.IGNORECASE)
    if bool(match):
      out.append(x)
  
  out = list(set(out))
  if len(out) == 0:
    return("unknown or Community Contribution")
  else:
    out = ", ".join(out)
    return(out)
  
def process_pubmed_results(results, trans):
  results['year'] = results['PubDate'].apply(lambda x: x.split()[0])
  x = ['FirstAuthorSurname', 'Source', 'year', 'PMID']
  results['name'] = results[x].apply(lambda row: " ".join([row['FirstAuthorSurname'], row['Source'], row['year'], row['PMID']]), axis = 1)
  results = results.rename(columns = metadata_translation)
  
  # guess at program label
  # results['program'] = 
  
  return(results)






# END
