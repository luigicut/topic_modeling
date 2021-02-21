# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%

import os
import gensim
import gensim.corpora as corpora
import spacy
import utils

from gensim.test.utils import datapath
from spacy.lang.en.stop_words import STOP_WORDS
#%%
project_url = ''
if 'PROJECT_URL' in os.environ:
    project_url = os.environ['PROJECT_URL']
project_name = project_url.split('/')[-1]

nlp= spacy.load("en_core_web_lg")
current_working_directory = os.getcwd()
stop_word = open("stop_word.txt", "r")
stop_list = stop_word.readline().split(",")
# Add project name sto stopwords
stop_list.append(project_name)
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

def process_file(file_name):
    os.chdir('committed_files')
    output_file = open(file_name,"r")

    #TODO: create function for these lines
    out=utils.license_remove(output_file.read())
    output_file.close()
    output_file = open(file_name,"w")
    output_file.write(out)
    output_file.close()
    output_file = open(file_name,"r")


    # os.chdir("../cleaned_committed_files")
    # corpus_file = open("cleaned_"+file_name+".txt","w")

    # READ THE WHOLE TEXT
    processed_corpus = utils.simpler_filter_text(str(output_file.read()))
    # corpus_file.write(processed_corpus+' ')


    output_file.close()
    # corpus_file.close()
    # corpus_file = open("cleaned_"+file_name+".txt","r")
    # processed_file = corpus_file.read()
    # corpus_file.close()
    os.chdir("..")
    return processed_corpus+' '

def make_prediction(project_name, processed_file):
    doc_list = []
    nlp.max_length = 5000000
    pr=nlp(str(processed_file))
    doc_list.append(pr)
    # Creates, which is a mapping of word IDs to words.
    words = corpora.Dictionary(doc_list)
    # Turns each document into a bag of words.
    corpus = [words.doc2bow(doc) for doc in doc_list]
    temp_file = "model_"+project_name
    lda = gensim.models.ldamodel.LdaModel.load(current_working_directory+'/GIT_CACHE/'+project_name+'_models'+'/gensim_model/'+temp_file)
    new_prediction= lda[corpus]
    new_prediction = new_prediction[0][2]
    words_concat = [[(words[id], freq) for id, freq in cp] for cp in corpus[:1]]
    words_concat = words_concat[0]
    final_prediction = []
    for i, elements in enumerate(words_concat):
        final_prediction.append((elements[0], new_prediction[i][1][0][1]))
    final_prediction = sorted(final_prediction, key=lambda x: (x[1]), reverse=True)
    return final_prediction
    


    
#%%
def make_joint_prediction(project_name, project_url, commit_sha):

    if not os.path.isfile('joint_corpus_'+commit_sha+".txt"):
        output_file = open("joint_corpus_"+commit_sha+".txt","a+",encoding="utf-8")
        for root, dirs, files in os.walk('committed_files'):
            for file in files:
                processed_file = process_file(file)
                output_file.write(processed_file)
        output_file.close()
    
    output_file = open("joint_corpus_"+commit_sha+".txt","r",encoding="utf-8")
    joint_file_prediction = make_prediction(project_name, output_file.read())

    return joint_file_prediction

