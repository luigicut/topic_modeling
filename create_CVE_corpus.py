# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import numpy as np
import pandas as pd
import re
import os
import requests
import yaml
import gensim
import gensim.corpora as corpora
import en_core_web_lg
import spacy
import json
import utils

from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
from gensim.test.utils import datapath
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en.stop_words import STOP_WORDS
from tqdm import tqdm_notebook as tqdm
from pprint import pprint
from collections import defaultdict
#%%

current_working_directory = os.getcwd()
output_file = open("CVE_corpus.txt","a+",encoding="utf-8")
# for root, dirs, files in os.walk('CVE_list'):
#     for file in files:
#         print(file)
#         with open(file) as f:
#           data = json.load(f)
#           for i in range(len(data['CVE_Items'])):
#   # print(data['CVE_Items'][i]['cve']['description']['description_data'][0]['value'])
#             output_file.write(data['CVE_Items'][i]['cve']['description']['description_data'][0]['value'])
# output_file.close()
with open('CVE_list/nvdcve-1.1-2011.json', encoding="utf8") as f:
  data = json.load(f)
for i in range(len(data['CVE_Items'])):
  description = data['CVE_Items'][i]['cve']['description']['description_data'][0]['value']
  # print(data['CVE_Items'][i]['cve']['description']['description_data'][0]['value'])
  if not '** REJECT **' in description:
    encoded_description = description.encode("utf-8")
    processed_description = utils.simpler_filter_text(str(encoded_description))
    processed_description_striped = processed_description.strip() 
    if processed_description_striped != '':
        output_file.write(processed_description_striped+' ')
    # output_file.write(description+' ')
  # print(data['CVE_Items'][i])
print('finished')
output_file.close()
#%%
import fasttext
import os,sys,inspect
# if not os.path.isfile("model"+cve+".bin"):
print("creating fasttext model")
model = fasttext.train_unsupervised('CVE_corpus.txt')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
model.save_model(currentdir+"/CVE_MODEL.bin")
# %%
model = fasttext.load_model(currentdir+"/CVE_MODEL.bin")
model.get_nearest_neighbors('injection')
# %%
