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

df = pd.read_csv("new_publications.csv")
n = df.shape[0] + 1
df['temp'] = [str(x) for x in range(1,n)]

new_pubs_name = df.loc[:, ['name', 'temp']]
new_pubs_name = new_pubs_name.set_index('temp')
new_pubs_name = new_pubs_name.to_dict('index')

df = df.drop(columns = ['name'])
new_pubs_dict = file_anno_to_dict(df, i = "temp")

syn = synapseclient.login()

for x in new_pubs_dict:
  file = File(name = new_pubs_name[x]['name'], parent_id = 'syn64427609', external_url = new_pubs_dict[x]['URL'][0])
  file.synapse_store = False
  file.force_version = False
  file.annotations = new_pubs_dict[x]
  file = file.store()


print("New publication entities added to ARK backend folder syn64427609")



# END
