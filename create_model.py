# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

# %%
import os
import yaml
import chardet
import spacy
import utils
import gensim
import gensim.corpora as corpora

from spacy.lang.en.stop_words import STOP_WORDS
from gensim.test.utils import common_texts
from gensim.corpora.dictionary import Dictionary
from gensim.test.utils import common_texts
from gensim.corpora.dictionary import Dictionary
from gensim.test.utils import datapath
from pprint import pprint


# %%
#DEFINE THE CVE 
cve = 'CVE-2020-10714'


# %%

#Retrieve project url associated to CVE in the relative yaml file
current_working_directory = os.getcwd()
statments_yaml = open("statements/"+cve+"/statement.yaml",'r')
parsed_statments =  yaml.load(statments_yaml, Loader=yaml.FullLoader)
project_url = ''

if  'fixes' in parsed_statments:
    project_url = parsed_statments['fixes'][0]['commits'][0]['repository']
else:
    raise SystemExit("please provide project name")

project_name=project_url.split('/')[-1]
print(project_name)

os.chdir('diff_commits/'+cve)
if not os.path.isfile('project_corpus.txt'):
    output_file = open("project_corpus.txt","a+",encoding="utf-8")
    #Check all the file from every directory from the project using os.walk excluding the following folders
    exclude_dir = set(['.git', '.vscode', '.idea'])
    for root, dirs, files in os.walk(project_name):
        dirs[:] = [d for d in dirs if d not in exclude_dir]
        for file in files:
            with open(os.path.join(root, file), "r", encoding="utf-8") as tmp_file:
                print(tmp_file.name)
                #Open file as byte to use it with chardet
                byte_tmp_file = open(os.path.join(root, file), "rb")
                #Using chardet prediction to exclude not ascii or utf8 files
                file_type = chardet.detect(byte_tmp_file.read())['encoding']
                print(file_type)
                #TODO: Remove None and type Windows-1254 (TIS-620 if this give no error)
                if str(file_type) == 'utf-8' or str(file_type) == 'ascii':
                    output_file.write(tmp_file.read()+' ')
                tmp_file.close()
                byte_tmp_file.close()
    output_file.close()

output_file = open("project_corpus.txt","r",encoding="utf-8")
os.chdir(current_working_directory)

# %%
nlp= spacy.load("en_core_web_sm")
# My list of stop words.
stop_word = open("stop_word.txt", "r")
stop_list = stop_word.readline().split(",")
# Updates spaCy's default stop words list with my additional words. 
nlp.Defaults.stop_words.update(stop_list)

# Iterates over the words in the stop words list and resets the "is_stop" flag.
for word in STOP_WORDS:
    lexeme = nlp.vocab[word]
    lexeme.is_stop = True

# %%
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
#REMOVING ALL SNAKE,CAMEL,DOT WORDS
os.chdir('diff_commits/'+cve)
if not os.path.isfile('project_corpus_cleaned.txt'):
    processed_corpus= utils.simpler_filter_text(str(output_file.read()))
    corpus_file = open("project_corpus_cleaned.txt","w",encoding="utf-8")
    corpus_file.write(processed_corpus)
    corpus_file.close()
output_file.close()
print("finished!")

# %%

nlp.max_length = 6000000
corpus_file = open("project_corpus_cleaned.txt","r",encoding="utf-8")
doc_list = []
pr=nlp(str(corpus_file.read()))
doc_list.append(pr)

# Creates, which is a mapping of word IDs to words.
words = corpora.Dictionary(doc_list)

corpus = [words.doc2bow(doc) for doc in doc_list]

lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                           id2word=words,
                                           num_topics=1, 
                                           random_state=2,
                                           update_every=1,
                                           passes=10,
                                           alpha='auto',
                                           per_word_topics=True)


#%%

os.chdir(current_working_directory)
temp_file = datapath("model")
lda_model.save(temp_file)
