# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

import os,sys,inspect
import yaml
import chardet
import spacy
import utils
import gensim
import gensim.corpora as corpora
import fasttext
import subprocess
# from tqdm import tqdm_notebook as tqdm
from tqdm import tqdm
from multiprocessing import Pool
# with_multiprocessing = True
# number_of_cpus = os.cpu_count()

from spacy.lang.en.stop_words import STOP_WORDS
from pprint import pprint
from datetime import datetime
# nlp = spacy.load("en_core_web_lg")

project_url = ''
if 'PROJECT_URL' in os.environ:
    project_url = os.environ['PROJECT_URL']
project_name = project_url.split('/')[-1]


def read_in_chunks(file_object, chunk_size):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def lemmatizer(doc):
    nlp = spacy.load("en_core_web_lg")
    # This takes in a doc of tokens from the NER and lemmatizes them. 
    # Pronouns (like "I" and "you" get lemmatized to '-PRON-', so I'm removing those.
    doc = [token.lemma_ for token in doc if token.lemma_ != '-PRON-']
    doc = ' '.join(doc)
    return nlp.make_doc(doc)
    
def remove_stopwords(doc):
    # This will remove stopwords and punctuation.
    # Use token.text to return strings, which we'll need for Gensim.
    doc = [token.text for token in doc if token.is_stop != True and token.is_punct != True]
    return doc


def text_into_chunks(text, chunk_size=1000):
    '''
    Yield successive n-sized chunks from list.
    '''
    if type(text) == list:
        text = ' '.join(text)
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def main(cve, number_of_cpus):
  print('main di FINAL_01_create_model_multip')
  #DEFINE THE CVE
  vulnerability_id = cve
  chunk_size = 1000000
  nlp2 = spacy.load("en_core_web_lg")
  nlp = spacy.load("en_core_web_lg")
  startTime = datetime.now()
  print('starting time: '+str(startTime))

  #Retrieve project url associated to CVE in the relative yaml file
  current_working_directory = os.getcwd()
  os.environ['GIT_CACHE'] = current_working_directory + "/GIT_CACHE"
  GIT_CACHE = os.environ['GIT_CACHE']
  statments_yaml = open(current_working_directory+"/statements/"+vulnerability_id+"/statement.yaml",'r')
  parsed_statments =  yaml.load(statments_yaml, Loader=yaml.FullLoader)
  project_url = ''

  if  'fixes' in parsed_statments:
      project_url = parsed_statments['fixes'][0]['commits'][0]['repository']
  else:
      raise SystemExit("please provide project name")

  project_name=project_url.split('/')[-1]
  if len(project_url.split('.')) > 1:
    if project_url.split('.')[-1] == 'git':
       os.environ['PROJECT_URL'] = '.'.join(project_url.split('.')[:-1])
       project_url = '.'.join(project_url.split('.')[:-1])
       project_name = project_name.split('.')[0]
  print(project_name)
  os.environ['PROJECT_URL'] = project_url


  

  # My list of stop words.
  stop_word = open("stop_word.txt", "r")
  stop_list = stop_word.readline().split(",")
  # Updates spaCy's default stop words list with my additional words. 
  nlp.Defaults.stop_words.update(stop_list)
  # Add project name sto stopwords
  # stop_list.append(project_name)

  # Iterates over the words in the stop words list and resets the "is_stop" flag.
  for word in STOP_WORDS:
      lexeme = nlp.vocab[word]
      lexeme.is_stop = True

  # The add_pipe function appends our functions to the default pipeline.
  nlp.add_pipe(lemmatizer,name='lemmatizer',after='ner')
  nlp.add_pipe(remove_stopwords, name="stopwords", last=True)
  
  os.chdir('GIT_CACHE/')
  if not os.path.isdir('./'+project_name+"_models"):
      print('create folder...')
      # creates a folder using project name to store project corpus and models
      os.mkdir(project_name+"_models")
      os.chdir(project_name+"_models")
  else:
      print('folder already exists')
      os.chdir(project_name+"_models")
      print('in folder: '+os.getcwd())

  if not os.path.isfile('project_corpus.txt'):
      output_file = open("project_corpus.txt","a+",encoding="utf-8")
      #git.Git().clone(project_url)
      #Check all the file from every directory from the project using os.walk excluding the following folders
      exclude_dir = set(['.git', '.vscode', '.idea'])
      for root, dirs, files in tqdm(os.walk(GIT_CACHE+"/"+project_name)):
          dirs[:] = [d for d in dirs if d not in exclude_dir]
          for file in files:
              with open(os.path.join(root, file), "r", encoding="utf-8") as tmp_file:
                  print(tmp_file.name)
                  file_name = tmp_file.name
                  #Open file as byte to use it with chardet
                  byte_tmp_file = open(os.path.join(root, file), "rb")
                  #Using chardet prediction to exclude not ascii or utf8 files
                  file_type = chardet.detect(byte_tmp_file.read())['encoding']
                  print(file_type)
                  # tmp_file = tmp_file.decode('utf-8','ignore').encode("utf-8")
                  #TODO: Remove None and type Windows-1254 (TIS-620, ISO-8859-1(html), if this give no error)
                  if str(file_type) == 'utf-8' or str(file_type) == 'ascii' or str(file_type) == 'TIS-620':
                      file_extension = file_name.split('.')[-1]
                      if str(file_type) == 'TIS-620' and not file_extension == 'java':
                          continue
                      output_file.write(tmp_file.read()+' ')
                  tmp_file.close()
                  byte_tmp_file.close()
      output_file.close()

  output_file = open("project_corpus.txt","r",encoding="utf-8")
  os.chdir(current_working_directory)






  #REMOVING ALL SNAKE,CAMEL,DOT WORDS
  os.chdir('GIT_CACHE/'+project_name+"_models")
  if not os.path.isfile('project_corpus_cleaned.txt'):
      text = str(output_file.read())
      # when a list is provided concatenate it into a string
      if type(text) == list:
          text = ' '.join([str(line) for line in text])
      os.chdir(current_working_directory)
      # chunk_List = list()
      # for chunk in tqdm(text_into_chunks(text, chunk_size = 500000)):
      #   chunk_List.append(nlp(chunk))
      input_list = [(nlp2(chunk), project_name, current_working_directory) for chunk in tqdm(text_into_chunks(text, chunk_size = 500000))]
      with Pool(number_of_cpus) as p:
        # filter text, needs to be in chunks due to spacy maximum of 1000000 characters
        result = p.starmap(utils.filterChunkDoc, input_list)
      endTime = datetime.now()
      print('started at: '+str(startTime))
      print('finished at: '+str(endTime))  
      processed_corpus =  ' '.join(result).lower()
      # processed_corpus= utils.simpler_filter_text(str(output_file.read()))
      print('OUT!')
      os.chdir(current_working_directory+'/GIT_CACHE/'+project_name+"_models")
      corpus_file = open("project_corpus_cleaned.txt","w",encoding="utf-8")
      corpus_file.write(processed_corpus)
      corpus_file.close()
  output_file.close()
  print("finished!")


  temp_file ="model_"+project_name
  if not os.path.exists("gensim_model"):
    os.mkdir("gensim_model")
  if not os.path.exists(current_working_directory+'/GIT_CACHE/'+project_name+"_models"+"/gensim_model/"+temp_file):
      nlp.max_length = 15000000
      doc_list = []
      words = corpora.Dictionary(doc_list)
      with open('project_corpus_cleaned.txt', "r", encoding='utf-8') as f:
          for piece in tqdm(read_in_chunks(f, chunk_size)):
              next_doc_list = []
              pr=nlp(str(piece))
              next_doc_list.append(pr)
              words.add_documents(next_doc_list)
              doc_list.extend(next_doc_list)
      flat_list = [[item for sublist in doc_list for item in sublist]]

      # Creates, which is a mapping of word IDs to words.
      # words = corpora.Dictionary(doc_list)
      corpus = [words.doc2bow(doc) for doc in flat_list]

      lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                              id2word=words,
                                              num_topics=1, 
                                              random_state=2,
                                              update_every=1,
                                              passes=10,
                                              alpha='auto',
                                              per_word_topics=True)

      pprint(lda_model.print_topics(num_words=40))
      lda_model.save(current_working_directory+'/GIT_CACHE/'+project_name+"_models"+"/gensim_model/"+temp_file)


  if not os.path.exists("fasttext_model"):
    os.mkdir("fasttext_model")
  os.chdir("fasttext_model/")
  fasttext_model_path = current_working_directory+'/GIT_CACHE/'+project_name+"_models"+'/fasttext_model'
  if not os.path.isfile("model_"+project_name+".bin"):
      os.chdir(current_working_directory+'/GIT_CACHE/'+project_name+"_models")
      print("creating fasttext model")
      model = fasttext.train_unsupervised('project_corpus_cleaned.txt')
      os.chdir("fasttext_model/")
      model.save_model(fasttext_model_path+"/model_"+project_name+".bin")
  else:
      print("model already exist, loading.")
      model = fasttext.load_model(fasttext_model_path+"/model_"+project_name+".bin")



  fasttext_model_path = current_working_directory+'/GIT_CACHE/'+project_name+"_models"+'/fasttext_model'
  gensim_model_path = current_working_directory+'/GIT_CACHE/'+project_name+"_models"+'/gensim_model'
  if os.path.isfile("model_"+project_name+".bin") and not os.path.isfile("model_"+project_name+".vec") :
      lines=[]
      # get all words from model
      words = model.get_words()
      with open(fasttext_model_path+"/model_"+project_name+".vec",'w',encoding='utf-8') as file_out:
          # the first line must contain number of total words and vector dimension
          file_out.write(str(len(words)) + " " + str(model.get_dimension()) + "\n")
          # line by line, you append vectors to VEC file
          for w in words:
              v = model.get_word_vector(w)
              vstr = ""
              for vi in v:
                  vstr += " " + str(vi)
              try:
                  file_out.write(w + vstr+'\n')
              except:
                  pass
  
  if not os.path.isdir(gensim_model_path+"/en_vectors_wiki_lg_"+project_name):
    #last GENSIM model for similarity
    os.chdir(fasttext_model_path)
    try:
        cmd = ["python", "-m", "spacy", "init-model", "en"]
        cmd.append("../gensim_model/en_vectors_wiki_lg_" + str(project_name))
        cmd.append("--vectors-loc")
        cmd.append("model_" + str(project_name) + ".vec")
        proc = subprocess.Popen(cmd, cwd=os.getcwd(), shell=True)
        out, err = proc.communicate()

        if proc.returncode != 0:
            print(err)
            raise Exception("Process (%s) exited with non-zero return code" % ' '.join(cmd))
    except subprocess.TimeoutExpired:
        print('Timeout exceeded')
        raise Exception('Process did not respond')


  os.chdir(current_working_directory)

if __name__ == "__main__":
  main()