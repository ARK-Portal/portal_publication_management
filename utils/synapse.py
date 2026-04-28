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


def get_ark_pubs():
  df = query("SELECT ")
  
