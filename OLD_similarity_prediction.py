# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import re
import spacy
import utils
import gather_commits
import topic_modeling_files
from tqdm import tqdm_notebook as tqdm
import os
import yaml

project_url = ''
if 'PROJECT_URL' in os.environ:
    project_url = os.environ['PROJECT_URL']
project_name = project_url.split('/')[-1]

current_working_directory = os.getcwd()

def main():
  vulnerability_id ="CVE-2015-6748"

  # nlp2 = spacy.load("en_core_web_lg")

  os.environ['GIT_CACHE'] = current_working_directory + "/GIT_CACHE"
  GIT_CACHE = os.environ['GIT_CACHE']
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
            commit_pred = topic_modeling_files.make_joint_prediction(project_name, project_url, commit)
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
      if os.path.exists(commit):
          prediction_joint_file = open(commit+"/prediction_joint_corpus_"+commit+".txt","r")
          prediction_words_list = re.findall(r"'(.*?)'", prediction_joint_file.read())[:LDA_WORDS_NUMBER-1]
          # print(str(prediction_words_list))
          similarity_avg = 0
          # if commit == "e07263dedad7ed44e188abb11260fa3061afadc4":
          for key in cve_keywords:
              max_value = -1
              for pred in prediction_words_list:
                  k = nlp(key)
                  p = nlp(pred)
                  if k.similarity(p) > max_value:
                      max_value = k.similarity(p)
              similarity_avg += max_value
          similarity_avg = similarity_avg/len(cve_keywords) 
          os.chdir(cve_path)   
          commits_similarity_file = open("commits_similarity_file.txt","a+")
          commits_similarity_file.writelines(commit+","+str(similarity_avg)+"\n")
  commits_similarity_file.close()


if __name__ == "__main__":
  main()
