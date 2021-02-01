# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import os
vulnerability_id ="CVE-2020-1961"
current_working_directory = os.getcwd()
os.environ['GIT_CACHE'] = current_working_directory + '/diff_commits/'+vulnerability_id

import numpy as np
import pandas as pd
import re
import requests
import yaml
import gensim
import gensim.corpora as corpora
import en_core_web_lg
import spacy
import utils
import chardet
import gather_commits
import topic_modeling_files

from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
from gensim.test.utils import datapath
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en.stop_words import STOP_WORDS
from tqdm import tqdm_notebook as tqdm
from pprint import pprint
from collections import defaultdict
# %%

current_working_directory = os.getcwd()
print(current_working_directory)
# %%
statments_yaml = open("statements/"+vulnerability_id+"/statement.yaml",'r')
parsed_statments =  yaml.load(statments_yaml, Loader=yaml.FullLoader)
project_url = ''
commit_sha = ''

if  'fixes' in parsed_statments:
    project_url = parsed_statments['fixes'][0]['commits'][0]['repository']
    commit_sha = parsed_statments['fixes'][0]['commits'][0]['id']
else:
    raise SystemExit("please provide project URL and fix commit SHA and restart")
# %%
os.chdir('diff_commits/'+vulnerability_id)
if not os.path.isdir('./candidate_commits'):
    print('create folder...')
    # creates a folder using CVE name
    os.mkdir('candidate_commits')
else:
    print('folder already exists')
os.chdir(current_working_directory)

#%%
#RETRIVING THE COMMIT LIST
commit_list = gather_commits.get_commit_list(vulnerability_id, project_url)
print(commit_list)
#CREATING A FOLDER FOR EACH COMMIT 
for commit in commit_list:
    os.chdir(current_working_directory+'/diff_commits/'+vulnerability_id+"/"+"candidate_commits")
    if not os.path.isdir(commit):
        os.mkdir(commit)
        os.chdir(commit)
        os.mkdir("committed_files")
        os.mkdir("cleaned_committed_files")
    else:
        os.chdir(commit)
    utils.extract_files_from_diff(project_url,commit, vulnerability_id)


# commit_pred = topic_modeling_files.make_joint_prediction(vulnerability_id, project_url, commit_sha)
# print(commit_pred)

# %%
# os.chdir('diff_commits/'+vulnerability_id+"/fasttext_model")
# nlp = spacy.load("en_vectors_wiki_lg"+vulnerability_id)

# doc1 = nlp("injections")
# doc2 = nlp("sections")



# %%

# print(doc1.similarity(doc2))

# %%