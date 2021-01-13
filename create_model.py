# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

# %%
import os
import yaml
import chardet
import spacy
import utils

from spacy.lang.en.stop_words import STOP_WORDS

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
#REMOVING ALL SNAKE,CAMEL,DOT WORDS
os.chdir('diff_commits/'+cve)
processed_corpus= utils.simpler_filter_text(str(output_file))
corpus_file = open("project_corpus_cleaned.txt","w")
corpus_file.write(processed_corpus)
corpus_file.close()
print("finished!")