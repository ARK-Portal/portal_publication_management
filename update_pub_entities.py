#! python

# create_new_pub_entities.py

# import necessary libraries
import sys
import os
import synapseclient
import pandas as pd
import synapseutils
from synapseclient.models import File

sys.path.append("utils")
from utils import file_anno_to_dict

df = pd.read_csv("publication_updates.csv")

pubs_name = df.loc[:, ['name', 'id']]
pubs_name = pubs_name.set_index('id')
pubs_name = pubs_name.to_dict('index')

df = df.drop(columns = ['name'])
pubs_dict = file_anno_to_dict(df, i = "id")

syn = synapseclient.login()

for synID in pubs_dict:
  file = File(id = synID, download_file = False).get()
  file.name = pubs_name[synID]['name']
  file.external_url = pubs_dict[synID]['URL'][0]
  file.synapse_store = False
  file.force_version = False
  pubs_dict[synID]['authors'] = ", ".join(pubs_dict[synID]['authors'])
  file.annotations = pubs_dict[synID]
  file = file.store()

print("Publication entities have been updated in Synapse")



# END
