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
#%%
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

# os.chdir('diff_commits')
# if not os.path.isdir('./'+cve):
#     print('create folder...')
#     # creates a folder using CVE name
#     os.mkdir(cve)
#     # get diff file from github website
#     url = project_url+"/commit/"+commit_sha+".diff"
#     r = requests.get(url, allow_redirects=True)
#     os.chdir(cve)
#     # create diff file with SHA name
#     to_create_file = open(commit_sha+'.diff', 'wb')
#     to_create_file.write(r.content)
#     to_create_file.close()
# else:
#     print('folder already exists')
#     os.chdir(cve)
#     print('in folder: '+os.getcwd())

#diff_file = open(commit_sha+'.diff', "r")


# %%

nlp= spacy.load("en_core_web_sm")
# os.chdir(current_working_directory)
# My list of stop words.
stop_word = open("stop_word.txt", "r")
stop_list = stop_word.readline().split(",")
# Updates spaCy's default stop words list with my additional words. 
nlp.Defaults.stop_words.update(stop_list)

# Iterates over the words in the stop words list and resets the "is_stop" flag.
for word in STOP_WORDS:
    lexeme = nlp.vocab[word]
    lexeme.is_stop = True

#%%
def lemmatizer(doc):
    # This takes in a doc of tokens from the NER and lemmatizes them. 
    # Pronouns (like "I" and "you" get lemmatized to '-PRON-', so I'm removing those.
    doc = [token.lemma_ for token in doc if token.lemma_ != '-PRON-']
    doc = u' '.join(doc)
    return nlp.make_doc(doc)
    
def remove_stopwords(doc):
    # This will remove stopwords and punctuation.
    # Use token.text to return strings, which we'll need for Gensim.
    doc = [token.text for token in doc if token.is_stop != True and token.is_punct != True]
    return doc

# The add_pipe function appends our functions to the default pipeline.
nlp.add_pipe(lemmatizer,name='lemmatizer',after='ner')
nlp.add_pipe(remove_stopwords, name="stopwords", last=True)


# %%

# def process_file(file_name):
#     print("File name :"+file_name+"\n" )
#     os.chdir('committed_files')
#     output_file = open(file_name,"r")
#     # os.chdir(current_working_directory)
#     output_file_encoded = output_file.read().encode("utf-8")
#     output_file.close()
#     processed_file= utils.simpler_filter_text(str(output_file_encoded))
#     corpus_file = open(file_name+"_cleaned.txt","w")
#     corpus_file.write(processed_file)
#     corpus_file.close()
#     os.chdir(current_working_directory)
#     return processed_file

def process_file(file_name):
    print("File name :"+file_name+"\n" )
    os.chdir('committed_files')
    output_file = open(file_name,"r")
    corpus_file = open(file_name+"_cleaned.txt","w")
    for line in output_file.readlines():
        if not line.isspace() and len(line) > 1:
            encoded_line = line.encode("utf-8")
            processed_line = utils.simpler_filter_text(str(encoded_line))
            processed_line_striped = processed_line.strip() 
            if processed_line_striped != '':
                corpus_file.write(processed_line_striped+' ')
    output_file.close()
    corpus_file.close()
    corpus_file = open(file_name+"_cleaned.txt","r")
    processed_file = corpus_file.read()
    corpus_file.close()
    os.chdir(current_working_directory)
    return processed_file

def make_prediction(processed_file):
    doc_list = []
    pr=nlp(str(processed_file))
    doc_list.append(pr)
    # Creates, which is a mapping of word IDs to words.
    words = corpora.Dictionary(doc_list)
    # Turns each document into a bag of words.
    corpus = [words.doc2bow(doc) for doc in doc_list]
    temp_file = datapath("model"+cve)
    lda = gensim.models.ldamodel.LdaModel.load(temp_file)
    new_prediction= lda[corpus]
    new_prediction = new_prediction[0][2]
    words_concat = [[(words[id], freq) for id, freq in cp] for cp in corpus[:1]]
    words_concat = words_concat[0]
    final_prediction = []
    for i, elements in enumerate(words_concat):
        final_prediction.append((elements[0], new_prediction[i][1][0][1]))
    final_prediction = sorted(final_prediction, key=lambda x: (x[1]), reverse=True)
    print(final_prediction)
    print("\n\n\n") 


    
#%%

os.chdir('diff_commits/'+cve)
output_file = open("joint_files.txt","a+",encoding="utf-8")
for root, dirs, files in os.walk('committed_files'):
    for file in files:
        processed_file = process_file(file)
        output_file.write(processed_file)
        make_prediction(processed_file)
        os.chdir(current_working_directory+'/diff_commits/'+cve)
        
output_file.close()
output_file = open("joint_files.txt","r",encoding="utf-8")
print("\n\n\n")
print("joint file prediction")
make_prediction(output_file.read())



#%%
# output_file = open("committed_file_1_FormAuthenticationMechanism.java","r")
# byte_tmp_file = open("committed_file_1_FormAuthenticationMechanism.java", "rb")
# file_type = chardet.detect(byte_tmp_file.read())['encoding']
# print(file_type)
# os.chdir(current_working_directory)


# %%
# output_file_encoded = output_file.read().encode("utf-8")
# output_file.close()



# %%

# nlp= spacy.load("en_core_web_sm")

# # My list of stop words.
# stop_word = open("stop_word.txt", "r")
# stop_list = stop_word.readline().split(",")
# # Updates spaCy's default stop words list with my additional words. 
# nlp.Defaults.stop_words.update(stop_list)

# # Iterates over the words in the stop words list and resets the "is_stop" flag.
# for word in STOP_WORDS:
#     lexeme = nlp.vocab[word]
#     lexeme.is_stop = True

# %%
#REMOVING ALL SNAKE,CAMEL,DOT WORDS
# os.chdir('diff_commits/'+cve)
# processed_commit= utils.simpler_filter_text(str(output_file_encoded))
# corpus_file = open(commit_sha+"_cleaned.diff","w")
# corpus_file.write(processed_commit)
# corpus_file.close()
# print(processed_commit)
# os.chdir(current_working_directory)







# %%
# doc_list = []
# pr=nlp(str(processed_commit))
# doc_list.append(pr)


# %%
# # Creates, which is a mapping of word IDs to words.
# words = corpora.Dictionary(doc_list)

# # Turns each document into a bag of words.
# corpus = [words.doc2bow(doc) for doc in doc_list]


# %%
# temp_file = datapath("model")
# lda = gensim.models.ldamodel.LdaModel.load(temp_file)

# pprint(lda.print_topics(num_words=40))

# # %%
# print([[(words[id], freq) for id, freq in cp] for cp in corpus[:1]])

# new_prediction= lda[corpus]

# # for  topic in new_prediction:
# #     pprint(topic)


# #%%

# new_prediction = new_prediction[0][2]
# words_concat = [[(words[id], freq) for id, freq in cp] for cp in corpus[:1]]
# words_concat = words_concat[0]
# final_prediction = []


# for i, elements in enumerate(words_concat):
#     final_prediction.append((elements[0], new_prediction[i][1][0][1]))
    

# print(final_prediction)

# %%
