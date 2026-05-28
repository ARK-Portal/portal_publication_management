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
  

  
  df['URL'] = [''.join(['https://doi.org/', x]) for x in df['DOI']]
  
  return(df)

def harmonize_pub_df(df, add = [None]):
  anno_template = get_ark_pub_anno_template()
  add = add + ['authors', 'name', 'associatedDataset', 'has_prePrint', 'has_correction', 'URL']
  add = list(set(add)) # remove duplicates
  add = [x for x in add if x is not None]
  add = [x for x in add if x not in list(anno_template.columns)]
  for a in add:
    anno_template[a] = [None]
  
  keep = [x for x in list(df.columns) if x in list(anno_template.columns)]
  keep = [x for x in keep if x is not None]
  keep.sort
  df = df.loc[:, keep]
  new = [x for x in list(anno_template.columns) if x not in list(df.columns)]
  new = [x for x in new if x is not None]
  if len(new) > 0:
    for n in new:
      df[n] = [None]*df.shape[0]
  
  # set consistent order of columns of final df
  order = list(df.columns)
  order.sort
  df = df.loc[:,order]
  return(df)


def file_anno_to_dict(df = None, fid = None, i = None):
  """Function to convert a csv of annotations into a dictoinary of dictionaries where 
  each sub-dictionary contains a set of annotation keys with values set as array 
  that can be looped over to annotate the Synapse identites listed in column 'i'"""
  
  # arg testing
  if i is None:
    #print("Error: 'i' must be defined where i is the string of the index column name")
    raise ValueError("'i' must be defined where i is the string of the index column name")
  
  if df is None and fid is None:
    raise ValueError("either 'df' or 'fid' must be defined along with 'i'.")
    
  # by allowing the option of specifying a df inplace of a fid
  # the user can do whatever preprocessing to the df before conversion to dict
  if df is None:
    print(f"reading df from {fid}")
    df = pd.read_csv(fid, dtype = "object")
  
  df.fillna('nan', inplace = True)
  df = df.set_index(i)
  file_anno = df.to_dict('index')
  
  for synID in file_anno:
    to_del = []
    for anno in file_anno[synID]:
      if file_anno[synID][anno] == 'nan':
        #print(f"{anno} is NaN and will be removed as an annotation")
        to_del.append(anno)
      
      file_anno[synID][anno] = str(file_anno[synID][anno])
      file_anno[synID][anno] = file_anno[synID][anno].replace(", ", ",")
      file_anno[synID][anno] = file_anno[synID][anno].replace(" ,", ",")
      file_anno[synID][anno] = file_anno[synID][anno].split(",")
      
      # remove lists that exceed current Synapse Max List Length
      if len(file_anno[synID][anno]) > 100:
        to_del.append(anno)
      
      # remove annotations that exceed current Synapse character limit
      if len(''.join(file_anno[synID][anno])) > 500:
        to_del.append(anno)
      
      #print(anno)
    to_del = list(set(to_del))
    for key in to_del:
      del file_anno[synID][key]
  
  return file_anno


# END
