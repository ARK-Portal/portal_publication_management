#! python

# utils.py

'''
general utility functions to support workflow execution
'''

import os
from dotenv import load_dotenv
import json
import pandas as pd
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

def get_ark_pub_anno_template():
  fid = "https://raw.githubusercontent.com/ARK-Portal/data_model/refs/heads/main/model_templates/ark.PublicationMetadataTemplate.csv"
  df = pd.read_csv(fid)
  if 'Component' in list(df.columns):
    df = df.drop(columns = ['Component'])
  return(df)

def guess_annotation(x, which = None):
  if which is None:
    print("need to define 'which', options are 'program', 'project'")
  
  with open('json/match_strings.json', 'r') as file:
    match_strings = json.load(file)[which]
  
  out = []
  for z in match_strings.keys():
    match = re.search(match_strings[z], x, flags=re.IGNORECASE)
    if bool(match):
      out.append(z)
  
  out = list(set(out))
  if len(out) == 0:
    return(None)
  else:
    out = ", ".join(out)
    return(out)

def guess_project(x):
  with open('json/match_strings.json', 'r') as file:
    match_strings = json.load(file)['project']
  
  out = []
  for project in match_strings.keys():
    match = re.search(match_strings[project], x, flags=re.IGNORECASE)
    if bool(match):
      out.append(project)
  
  out = list(set(out))
  if len(out) == 0:
    return(None)
  else:
    out = ", ".join(out)
    return(out)

def guess_pubType(title, journal):
  x = '|'.join([title, journal])
  match_strings = {"correction": "Publisher Correction|Author Correction", 
                   "pre-print": "Biorxiv|Medrxiv"}
  out = []
  for pubtype in match_strings:
    match = re.search(match_strings[pubtype], x, flags=re.IGNORECASE)
    if bool(match):
      out.append(pubtype)
  
  out = list(set(out))
  if len(out) == 0:
    return('peer-reviewed')
  else:
    out = ", ".join(out)
    return(out)

def finalize_pub_metadata(df):
  ## guess at program label
  df['program'] = df['authors'].apply(lambda x:guess_annotation(x, which = "program"))
  df['project'] = df['title'].apply(lambda x:guess_annotation(x, which = "project"))
  df['URL'] = [''.join(["https://doi.org/", x]) if re.search('10', x) else None for x in df['DOI']]
  ## guess at publicationType
  x = list(map(lambda x, y: '|'.join([x,y]), list(df.title), list(df.journal)))
  df['publicationType'] = list(map(lambda x, y: guess_pubType(x, y), list(df.title), list(df.journal)))
  
  anno_template = get_ark_pub_anno_template()
  anno_template['authors'] = [None]
  anno_template['name'] = [None]
  keep = [x for x in list(df.columns) if x in list(anno_template.columns)]
  df = df.loc[:, keep]
  add = [x for x in list(anno_template.columns) if x not in list(df.columns)]
  
  df['URL'] = [''.join(['https://doi.org/', x]) for x in df['DOI']]
  
  return(df)



# END
