#! python

# portal_publications_update.py

import sys
import synapseclient
import os.path
import pandas as pd
import synapseutils
import re
from synapseclient.models import query, Table, Column, ColumnType

syn = synapseclient.login()

def prep_df (df, listColumns):
  # prep annotations 
  df = df.fillna("")
  for c in listColumns:
    if c in df.columns:
      #out = df[c].apply(lambda x: str(x))
      out = [str(x).replace(", ", ",") for x in list(df[c])]
      out = [x.split(",") for x in out]
      #out = df[c].apply(lambda x: str(x).replace(", ", ","))
      #out = df[c].apply(lambda x: x.split(","))
      out = [None if x == [''] else x for x in out]
      df[c] = out
  return df

# get portal pubs Table
portal_publications = Table(id = "syn71306282").get()

# query FileView to get all publication entities with DOI
all_publications = query("SELECT * from syn64429484")
all_publications = all_publications[all_publications.DOI.str.match("^10") == True]
all_publications = all_publications[all_publications['authors'].str.len() > 0]
all_publications.reset_index(drop=True, inplace = True)

keep = list(portal_publications.columns)
all_publications = all_publications.loc[:, keep]

# wrangle data for Table upsert
## determine which Table columns are LIST types
listColumns = []
for col in portal_publications.columns:
  column_type = portal_publications.columns[col].column_type
  match = re.search("LIST", column_type)
  if match:
    listColumns.append(col)

## drop any columns that are already lists
keep = []
for c in listColumns:
  if not isinstance(all_publications[c][0], list):
    keep.append(c)

listColumns = keep
all_publications = prep_df(df = all_publications, listColumns = listColumns)

# upsert to update portal
portal_publications.upsert_rows(values=all_publications, primary_keys=["id"])

print(f"{all_publications.shape[0]} publications added or updated in Portal-Publications Table.")

# END
