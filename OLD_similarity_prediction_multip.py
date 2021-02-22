# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import re
import spacy
import utils
import gather_commits
import gensim
import gensim.corpora as corpora
# from tqdm import tqdm_notebook as tqdm
from tqdm import tqdm
from datetime import datetime
import os

from gensim.test.utils import datapath
from spacy.lang.en.stop_words import STOP_WORDS

project_url = ''
if 'PROJECT_URL' in os.environ:
    project_url = os.environ['PROJECT_URL']
project_name = project_url.split('/')[-1]


# current_working_directory = os.getcwd()
# os.environ['GIT_CACHE'] = current_working_directory + "/GIT_CACHE"
from multiprocessing import Pool
number_of_cpus = os.cpu_count()
startTime = datetime.now()
print('starting time: '+str(startTime))

# nlp= spacy.load("en_core_web_lg")
# stop_word = open(current_working_directory+"/stop_word.txt", "r")
# stop_list = stop_word.readline().split(",")
# # Add project name sto stopwords
# stop_list.append(project_name)
# # Updates spaCy's default stop words list with my additional words. 
# nlp.Defaults.stop_words.update(stop_list)

# Iterates over the words in the stop words list and resets the "is_stop" flag.
# for word in STOP_WORDS:
#     lexeme = nlp.vocab[word]
#     lexeme.is_stop = True

import yaml


def lemmatizer(doc):
    nlp = spacy.load("en_core_web_lg")
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

def make_prediction(project_name, processed_file, nlp, current_working_directory):
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

def text_into_chunks(text, chunk_size=1000):
    '''
    Yield successive n-sized chunks from list.
    '''
    if type(text) == list:
        text = ' '.join(text)
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def process_file(file_name, nlp):
    os.chdir('committed_files')
    output_file = open(file_name,"r")
    nlp2 = spacy.load("en_core_web_lg")
    #TODO: create function for these lines
    out=utils.license_remove(output_file.read())
    output_file.close()
    output_file = open(file_name,"w")
    output_file.write(out)
    output_file.close()
    output_file = open(file_name,"r")


    # os.chdir("../cleaned_committed_files")
    # corpus_file = open("cleaned_"+file_name+".txt","w")

    text = str(output_file.read())

    # when a list is provided concatenate it into a string
    if type(text) == list:
        text = ' '.join([str(line) for line in text])

    with Pool(number_of_cpus) as p:
      # filter text, needs to be in chunks due to spacy maximum of 1000000 characters
      result = p.map(utils.filterChunkDoc, [nlp2(chunk) for chunk in tqdm(text_into_chunks(text, chunk_size = 500000))])

 
    processed_corpus =  ' '.join(result).lower()
    # processed_corpus= utils.simpler_filter_text(str(output_file.read()))
    print('OUT!')
    output_file.close()
    # READ THE WHOLE TEXT
    # processed_corpus = utils.simpler_filter_text(str(output_file.read()))
    # corpus_file.write(processed_corpus+' ')
    # corpus_file.close()
    # corpus_file = open("cleaned_"+file_name+".txt","r")
    # processed_file = corpus_file.read()
    # corpus_file.close()
    os.chdir("..")
    return processed_corpus+' '

def make_joint_prediction(project_name, project_url, commit_sha, nlp, current_working_directory):

    if not os.path.isfile('joint_corpus_'+commit_sha+".txt"):
        output_file = open("joint_corpus_"+commit_sha+".txt","a+",encoding="utf-8")
        for root, dirs, files in os.walk('committed_files'):
            for file in files:
                processed_file = process_file(file, nlp)
                output_file.write(processed_file)
        output_file.close()
        endTime = datetime.now()
        print('started at: '+str(startTime))
        print('finished at: '+str(endTime)) 
    
    output_file = open("joint_corpus_"+commit_sha+".txt","r",encoding="utf-8")
    joint_file_prediction = make_prediction(project_name, output_file.read(), nlp, current_working_directory)

    return joint_file_prediction

def main():

  current_working_directory = os.getcwd()
  # os.environ['GIT_CACHE'] = current_working_directory + "/GIT_CACHE"
  
  
  vulnerability_id ="CVE-2015-6748"


  os.environ['GIT_CACHE'] = current_working_directory + "/GIT_CACHE"
  GIT_CACHE = os.environ['GIT_CACHE']
  # startTime = datetime.now()
  # print('starting time: '+str(startTime))
  statments_yaml = open("statements/"+vulnerability_id+"/statement.yaml",'r')
  parsed_statments =  yaml.load(statments_yaml, Loader=yaml.FullLoader)
  project_url = ''
  commit_sha = ''

  if  'fixes' in parsed_statments:
      project_url = parsed_statments['fixes'][0]['commits'][0]['repository']
      commit_sha = parsed_statments['fixes'][0]['commits'][0]['id']
      os.environ['PROJECT_URL'] = project_url
  else:
      raise SystemExit("please provide project URL and fix commit SHA and restart")

  project_name=project_url.split('/')[-1]
  print(project_name)


  nlp= spacy.load("en_core_web_lg")
  
  nlp.add_pipe(remove_stopwords, name="stopwords", last=True)

  
  stop_word = open(current_working_directory+"/stop_word.txt", "r")
  stop_list = stop_word.readline().split(",")
  # Add project name sto stopwords
  stop_list.append(project_name)
  # Updates spaCy's default stop words list with my additional words. 
  nlp.Defaults.stop_words.update(stop_list)


  for word in STOP_WORDS:
    lexeme = nlp.vocab[word]
    lexeme.is_stop = True

  nlp.add_pipe(lemmatizer,name='lemmatizer',after='ner')



  LDA_WORDS_NUMBER = 50

  os.chdir('diff_commits/')
  if not os.path.isdir('./'+vulnerability_id):
      print('create folder...')
      # creates a folder using CVE name
      os.mkdir(vulnerability_id)
      os.chdir(vulnerability_id)
  else:
      print('folder already exists')
      os.chdir(vulnerability_id)
      print('in folder: '+os.getcwd())

  # if not os.path.isdir('./candidate_commits'):
  #     print('create folder...')
  #     # creates a folder using CVE name
  #     os.mkdir('candidate_commits')
  # else:
  #     print('folder already exists')
      
  os.chdir(current_working_directory)
  # candidate_commits_path = current_working_directory+'/diff_commits/'+vulnerability_id+"/"+"candidate_commits"
  vulnerability_path = current_working_directory+'/diff_commits/'+vulnerability_id

  #RETRIVING THE COMMIT LIST
  commit_list = gather_commits.get_commit_list(vulnerability_id, project_url)
  print(len(commit_list))

  #SAVE CANDIDATE COMMIT LIST FOR SPECIFIC VULNERABILITY
  os.chdir(vulnerability_path)
  commit_list_file = open("candidate_commits_"+vulnerability_id+".txt","w")
  for commit in commit_list:
      commit_list_file.writelines(str(commit)+"\n")
  commit_list_file.close()

  print('list saved')
  # commit_list = ['e07263dedad7ed44e188abb11260fa3061afadc4']

  #CREATE PROJECT COMMITS LIST
  project_commits_path = GIT_CACHE+"/"+project_name+"_commits"
  if not os.path.isdir(project_commits_path):
    os.mkdir(project_commits_path)
  os.chdir(project_commits_path)

  #CREATING A FOLDER FOR EACH COMMIT
  for commit in tqdm(commit_list):
      os.chdir(project_commits_path)
      if not os.path.isdir(commit):
          os.mkdir(commit)
          os.chdir(commit)
          os.mkdir("committed_files")
          # os.mkdir("cleaned_committed_files")
          utils.extract_files_from_diff(project_url,commit)
          utils.folder_cleaner(commit, project_commits_path)
          if os.path.exists(commit):
            print("processing commit : "+commit)
            os.chdir(project_commits_path+"/"+commit)
            commit_pred = make_joint_prediction(project_name, project_url, commit, nlp, current_working_directory)
            prediction_joint_file = open("prediction_joint_corpus_"+commit+".txt","w")
            for item in commit_pred:
                prediction_joint_file.writelines(str(item)+"\n")
            prediction_joint_file.close()
            # endTime = datetime.now()
            # print('finished at: '+str(endTime))
      else:
          print("commit folder already exist or it's empty")
      # utils.extract_files_from_diff(project_url,commit, vulnerability_id)
      
  # os.chdir(candidate_commits_path)
  # for commit in tqdm(commit_list):
  #     os.chdir(candidate_commits_path)
  #     if os.path.exists(commit):
  #         print("processing commit : "+commit)
  #         os.chdir(candidate_commits_path+"/"+commit)
  #         commit_pred = topic_modeling_files.make_joint_prediction(vulnerability_id, project_url, commit)
  #         prediction_joint_file = open("prediction_joint_corpus_"+commit+".txt","w")
  #         for item in commit_pred:
  #             prediction_joint_file.writelines(str(item)+"\n")
  #         prediction_joint_file.close()


  cve_path = current_working_directory+'/diff_commits/'+vulnerability_id
  os.chdir(cve_path)
  nlp = spacy.load(current_working_directory+"/GIT_CACHE/"+project_name+"_models/"+"gensim_model/en_vectors_wiki_lg_"+project_name)
  # os.chdir(candidate_commits_path)
  # os.chdir("..")
  cve_keywords = list()
  with open("cve_description_keywords.txt","r") as cve_keywords_file:
      cve_keywords = cve_keywords_file.readlines()
  # you may also want to remove whitespace characters like `\n` at the end of each line
  cve_keywords = [x.strip() for x in cve_keywords] 
  print(str(cve_keywords))
  # os.chdir(candidate_commits_path)
  for commit in commit_list:
      os.chdir(project_commits_path)
      # print('project_commits_path: '+project_commits_path)
      if os.path.exists(commit):
        if commit == "00c8d2b7623259246c4eb5df63494c6b42c08f85":
          # print('commit: '+commit)
          prediction_joint_file = open(project_commits_path+"/"+commit+"/prediction_joint_corpus_"+commit+".txt","r")
          # print('prediction_joint_file: '+prediction_joint_file.read())
          prediction_words_list = re.findall(r"'(.*?)'", prediction_joint_file.read())[:LDA_WORDS_NUMBER-1]
          # print('prediction_words_list: '+str(prediction_words_list))
          # print(str(prediction_words_list))
          similarity_avg = 0
          for key in cve_keywords:
              max_value = -1
              for pred in prediction_words_list:
                  k = nlp(key)
                  p = nlp(pred)
                  kSimP = k.similarity(p)
                  if k.similarity(p) > max_value:
                      max_value = k.similarity(p)
              similarity_avg += max_value
          similarity_avg = similarity_avg/len(cve_keywords) 
          os.chdir(cve_path)   
          commits_similarity_file = open("commits_similarity_file.txt","a+")
          commits_similarity_file.writelines(commit+","+str(similarity_avg)+"\n")
  commits_similarity_file.close()
  endTime = datetime.now()

  print('started at: '+str(startTime))
  print('finished at: '+str(endTime))


if __name__ == "__main__":
  main()
