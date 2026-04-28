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
