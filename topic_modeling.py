# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import numpy as np
import pandas as pd
import re

import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel

import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en.stop_words import STOP_WORDS
import en_core_web_lg

from tqdm import tqdm_notebook as tqdm
from pprint import pprint


# %%
#CONSIDERING ONLY LINES STARTING WITH "-" or "+" AND REMOVING LINES STARTING WITH "NOT_ALLOWED" WORDS
diffprova = open("filediffvero.diff", "r")
output_file = open("filediffsolocommit.diff","w")
not_allowed=["---","+++","-/*","- *","import","-#","+/*","+ *","+#","+package","-package","@"]
for line in diffprova.readlines():
    if (line.startswith('-') or line.startswith('+')):
            if not any(not_allowed in line for not_allowed in not_allowed):
                #way to do multiple sub in a single sentence
                rep = {"Set<": " ", "Pair<": " ","Field>>>": " "} 
                rep = dict((re.escape(k), v) for k, v in rep.items()) 
                pattern = re.compile("|".join(rep.keys()))
                line_no_set_pair = pattern.sub(lambda m: rep[re.escape(m.group(0))], line)
                line_no_html_tags= re.sub(r'<.*?>', '',line_no_set_pair)
                #REMOVE EMPTY LINES
                if (len(line_no_html_tags.split())> 1):
                    #ASSUMING THAT THE FIRST CHAR IS ALWAYS A "+" OR "-" WE'RE REMOVING IT
                    cleaned_line = line_no_html_tags[1:]
                    #REMOVING LEADING SPACES
                    cleaned_line = cleaned_line.strip()
                    output_file.write(cleaned_line)
output_file.close()


# %%
output_file = open("filediffsolocommit.diff","r")
#print(output_file.read())


# %%
diff_prova_vera= output_file.read().encode("utf-8")
#print()


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
def camel_case_split(token):
    '''
    Splits a CamelCase token into a list of tokens,

    Input:
        token (str): the token that should be split if it is in CamelCase

    Returns:
        None: if the token is not in CamelCase
        list: 'CamelCase' --> ['CamelCase', 'camel', 'case']
    '''
    if type(token) != str:
        raise TypeError('The provided token should be a str data type but is of type {}.'.format(type(token)))

    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', token)
    result = [m.group(0).lower() for m in matches]
    if len(result) == 1:
        return
    return [token] + result


# %%
def snake_case_split(token):
    '''
    Splits a snake_case token into a list of tokens,

    Input:
        token (str): the token that should be split if it is in CamelCase

    Returns:
        None: if the token is not in CamelCase
        list: 'CamelCase' --> ['CamelCase', 'camel', 'case']
    '''
    if type(token) != str:
        raise TypeError('The provided token should be a str data type but is of type {}.'.format(type(token)))

    result = token.split('_')
    if len(result) == 1:
        return 
    return [token] + result


# %%
def dot_case_split(token):
    '''
    Splits a dot.case token into a list of tokens,

    Input:
        token (str): the token that should be split if it is in dot.case

    Returns:
        None: if the token is not in dot.case
        list: 'dot.case' --> ['dot.case', 'dot', 'case']
    '''
    if type(token) != str:
        raise TypeError('The provided token should be a str data type but is of type {}.'.format(type(token)))

    result = token.split('.')
    if len(result) == 1:
        return 
    return [token] + result


# %%
def filter_doc(doc):
    if type(doc) != spacy.tokens.doc.Doc:
        raise TypeError("The document should be a spacy.tokens.doc.Doc, which is created by means of nlp(")
    
    tokens = [token for token in doc if token.is_punct == False and token.is_stop == False and any(char for char in token.text if char.isalpha()) and len(token) > 1] #token.pos_ in ['VERB', 'NOUN', 'PROPN', 'ADJ'] and 
    result = list()
    for token in tokens:
        if camel_case_split(token.text):
            result += [camel_case_token.lemma_ for camel_case_token in nlp(' '.join(camel_case_split(token.text)))]
        elif snake_case_split(token.text):
            result += [snake_case_token.lemma_ for snake_case_token in nlp(' '.join(snake_case_split(token.text)))]
        elif dot_case_split(token.text):
            result += [dot_case_token.lemma_ for dot_case_token in nlp(' '.join(dot_case_split(token.text)))]

        else:
            result.append(str(token.lemma_).lower())

    return ' '.join(result)


# %%
def text_into_chunks(text, chunk_size=1000):
    '''
    Yield successive n-sized chunks from list.
    '''
    if type(text) == list:
        text = ' '.join(text)
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


# %%
def simpler_filter_text(text):
    ''' Similar to filter_text but without options:
            will be lemmatized and returned as a string
    '''

    # when a list is provided concatenate it into a string
    if type(text) == list:
        text = ' '.join([str(line) for line in text])

    # filter text, needs to be in chunks due to spacy maximum of 1000000 characters
    return ' '.join([filter_doc(nlp(chunk)) for chunk in text_into_chunks(text, chunk_size = 10000)]).lower()


# %%
#REMOVING ALL SNAKE,CAMEL,DOT WORDS
processed_commit= simpler_filter_text(str(diff_prova_vera))

#REMOVING BREAKLINE
processed_commit= processed_commit.replace(r'/(\r\n|\n|\r)/gm', "")

#REMOVING SPECIAL CHARACTER
#processed_commit=re.sub('/^[a-z\d\-_\s]+$/i', '', processed_commit)
processed_commit=re.sub('[^a-zA-Z \n\.]', ' ', processed_commit) 


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
#doc_list = []
# Iterates through each article in the corpus.
#for doc in tqdm(newest_doc):
    # Passes that article through the pipeline and adds to a new list.
    #pr = nlp(doc)
    #doc_list.append(pr)


# %%
doc_list = []
pr=nlp(str(processed_commit))
doc_list.append(pr)


# %%
# Creates, which is a mapping of word IDs to words.
words = corpora.Dictionary(doc_list)

# Turns each document into a bag of words.
corpus = [words.doc2bow(doc) for doc in doc_list]


# %%
lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                           id2word=words,
                                           num_topics=1, 
                                           random_state=2,
                                           update_every=1,
                                           passes=10,
                                           alpha='auto',
                                           per_word_topics=True)


# %%
pprint(lda_model.print_topics(num_words=40))


# %%



