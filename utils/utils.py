#! python

# utils.py

'''
general utility funcitons to support workflow execution
'''

import os
from dotenv import load_dotenv

def get_ncbi_api_key():
  # Load local .env file (if it exists)
  load_dotenv()
  
  # Access variables (works locally and in GitHub Actions)
  ncbiapikey = os.getenv("NCBI_API_KEY")
  
  if not ncbiapikey:
    raise Exception("NCBI_API_KEY not found!")
  else:
    return(ncbiapikey)
