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
import utils
import chardet

from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
from gensim.test.utils import datapath
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en.stop_words import STOP_WORDS
from tqdm import tqdm_notebook as tqdm
from pprint import pprint
from collections import defaultdict
# %%
cve = 'CVE-2020-1961'

current_working_directory = os.getcwd()
print(current_working_directory)
# %%
statments_yaml = open("statements/"+cve+"/statement.yaml",'r')
parsed_statments =  yaml.load(statments_yaml, Loader=yaml.FullLoader)
project_url = ''
commit_sha = ''

if  'fixes' in parsed_statments:
    project_url = parsed_statments['fixes'][0]['commits'][0]['repository']
    commit_sha = parsed_statments['fixes'][0]['commits'][0]['id']
else:
    raise SystemExit("please provide project URL and fix commit SHA and restart")

# %%
os.chdir('diff_commits/'+cve+"/fasttext_model")
nlp = spacy.load("en_vectors_wiki_lgCVE-2020-1961")

doc1 = nlp("injections")
doc2 = nlp("sections")


# %%

print(doc1.similarity(doc2))

# %%