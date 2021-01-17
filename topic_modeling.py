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

from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
from gensim.test.utils import datapath
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en.stop_words import STOP_WORDS
from tqdm import tqdm_notebook as tqdm
from pprint import pprint
#%%
cve = 'CVE-2020-10714'


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

os.chdir('diff_commits')
if not os.path.isdir('./'+cve):
    print('create folder...')
    # creates a folder using CVE name
    os.mkdir(cve)
    # get diff file from github website
    url = project_url+"/commit/"+commit_sha+".diff"
    r = requests.get(url, allow_redirects=True)
    os.chdir(cve)
    # create diff file with SHA name
    to_create_file = open(commit_sha+'.diff', 'wb')
    to_create_file.write(r.content)
    to_create_file.close()
else:
    print('folder already exists')
    os.chdir(cve)
    print('in folder: '+os.getcwd())

diff_file = open(commit_sha+'.diff', "r")


# diff_file = open(commit_sha+'.diff', 'wb').write(r.content)
# os.chdir(current_working_directory)
# %%
# CONSIDERING ONLY LINES STARTING WITH "-" or "+" AND REMOVING LINES STARTING WITH "NOT_ALLOWED" WORDS
# diff_file = open("filediffvero.diff", "r")
output_file = open(commit_sha+"_cleaned.diff","w")
not_allowed=["---","+++","-/*","- *","import","-#","+/*","+ *","+#","+package","-package","@"]
for line in diff_file.readlines():
    if (line.startswith('-') or line.startswith('+')):
            if not any(not_allowed in line for not_allowed in not_allowed):
                #way to do multiple sub in a single sentence
                # rep = {"Set<": " ", "Pair<": " ","Field>>>": " "} 
                # rep = dict((re.escape(k), v) for k, v in rep.items()) 
                # pattern = re.compile("|".join(rep.keys()))
                # line_no_set_pair = pattern.sub(lambda m: rep[re.escape(m.group(0))], line)
                line_no_html_tags= re.sub(r'<.*?>', '',line)
                #REMOVE EMPTY LINES
                if (len(line_no_html_tags.split())> 1):
                    #ASSUMING THAT THE FIRST CHAR IS ALWAYS A "+" OR "-" WE'RE REMOVING IT
                    cleaned_line = line_no_html_tags[1:]
                    #REMOVING LEADING SPACES
                    cleaned_line = cleaned_line.strip()
                    output_file.write(cleaned_line)
output_file.close()


# %%
output_file = open(commit_sha+"_cleaned.diff","r")
#print(output_file.read())
#returning to root directory
os.chdir(current_working_directory)

# %%
output_file_encoded = output_file.read().encode("utf-8")
output_file.close()



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
#REMOVING ALL SNAKE,CAMEL,DOT WORDS
os.chdir('diff_commits/'+cve)
processed_commit= utils.simpler_filter_text(str(output_file_encoded))
corpus_file = open(commit_sha+"_cleaned.diff","w")
corpus_file.write(processed_commit)
corpus_file.close()
print(processed_commit)
os.chdir(current_working_directory)
#REMOVING BREAKLINE
# processed_commit= processed_commit.replace(r'/(\r\n|\n|\r)/gm', " ")

#REMOVING SPECIAL CHARACTER
#processed_commit=re.sub('/^[a-z\d\-_\s]+$/i', '', processed_commit)
# processed_commit=re.sub('[^a-zA-Z \n\.]', ' ', processed_commit) 


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
# lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
#                                            id2word=words,
#                                            num_topics=1, 
#                                            random_state=2,
#                                            update_every=1,
#                                            passes=10,
#                                            alpha='auto',
#                                            per_word_topics=True)


# %%
#pprint(lda_model.print_topics(num_words=40))


# %%
temp_file = datapath("model")
lda = gensim.models.ldamodel.LdaModel.load(temp_file)

pprint(lda.print_topics(num_words=40))
# def process_query(query):
#     words = []
#     words = query.split()
#     return words

# query_corpus= process_query(processed_commit)

# %%
print([[(words[id], freq) for id, freq in cp] for cp in corpus[:1]])

new_prediction= lda[corpus]

for  topic in new_prediction:
    pprint(topic)



# %%
# word_count_array = np.empty((len(new_prediction), 2), dtype = np.object)
# for i in range(len(new_prediction)):
#     word_count_array[i, 0] = new_prediction[i][0]
#     word_count_array[i, 1] = new_prediction[i][1]

# idx = np.argsort(word_count_array[:, 1])
# idx = idx[::-1]
# word_count_array = word_count_array[idx]

# final = []
# final = lda.print_topic(word_count_array[0, 0], 1)

# question_topic = final.split('*')

# print(question_topic[1])
 
#%% 

# def format_topics_sentences(ldamodel=lda, corpus=corpus):
#     # Init output
#     sent_topics_df = pd.DataFrame()

#     # Get main topic in each document
#     for i, row in enumerate(ldamodel[corpus]):
#         row = sorted(row, key=lambda x: (x[0]), reverse=True)
#         # Get the Dominant topic, Perc Contribution and Keywords for each document
#         for j, (topic_num, prop_topic) in enumerate(row):
#             if j == 0:  # => dominant topic
#                 wp = ldamodel.show_topic(topic_num)
#                 topic_keywords = ", ".join([word for word, prop in wp])
#                 sent_topics_df = sent_topics_df.append(pd.Series([int(topic_num), round(prop_topic,4), topic_keywords]), ignore_index=True)
#             else:
#                 break
#     sent_topics_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords']

#     # Add original text to the end of the output
#     # contents = pd.Series(texts)
#     # sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
#     return(sent_topics_df)


# df_topic_sents_keywords = format_topics_sentences(ldamodel=lda, corpus=corpus)

# # Format
# df_dominant_topic = df_topic_sents_keywords.reset_index()
# df_dominant_topic.columns = ['Document_No', 'Dominant_Topic', 'Topic_Perc_Contrib', 'Keywords', 'Text']

# # Show
# df_dominant_topic.head(10)

