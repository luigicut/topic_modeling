import os, spacy, yaml, re


def main(cve):
  vulnerability_id =cve
  current_working_directory = os.getcwd()

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
  if len(project_url.split('.')) > 1:
    if project_url.split('.')[-1] == 'git':
      project_url = '.'.join(project_url.split('.')[:-1])
      project_name = project_name.split('.')[0]
  print(project_name)

  LDA_WORDS_NUMBER = 50

  project_commits_path = GIT_CACHE+"/"+project_name+"_commits"
  cve_path = current_working_directory+'/diff_commits/'+vulnerability_id
  os.chdir(cve_path)
  nlp = spacy.load(current_working_directory+"/GIT_CACHE/"+project_name+"_models/"+"gensim_model/en_vectors_wiki_lg_"+project_name)

  cve_keywords = list()
  with open("cve_description_keywords.txt","r") as cve_keywords_file:
      cve_keywords = cve_keywords_file.readlines()
  # you may also want to remove whitespace characters like `\n` at the end of each line
  cve_keywords = [x.strip() for x in cve_keywords] 
  print(str(cve_keywords))

  commit_list = list()
  with open("candidate_commits_"+vulnerability_id+".txt","r") as commit_list_file:
      commit_list = commit_list_file.readlines()
  # you may also want to remove whitespace characters like `\n` at the end of each line
  commit_list = [x.strip() for x in commit_list] 
  print(commit_list)
  for commit in commit_list:
      os.chdir(project_commits_path)
      # print('project_commits_path: '+project_commits_path)
      if os.path.exists(commit):
        # if commit == "00c8d2b7623259246c4eb5df63494c6b42c08f85":
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
  os.chdir(current_working_directory)
