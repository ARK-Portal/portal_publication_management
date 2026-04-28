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

for d in doi:
  query = ["https://api.crossref.org/works/doi/", d]
  query = ''.join(query)
  query_response = requests.get(query)
  results = json.loads(query_response.content)







# END
