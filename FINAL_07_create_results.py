
#per ogni CVE, prendere i commit rilevati negli statements
  #per ogni commit rilevato, cercare nel file delle prediction ordinate (il file delle
  # prediction ordinate deve diventare una lista di tuple), quel commit
  # prendere il valore di similarità di quel commit

  #normalizzare il valore di similarità di quel commit basandosi sul massimo valore sul file della prediction 
  # salvare in un file di RESULTS una row con la CVE, il commit e il valore di similarity normalizzato
  #fare la stessa cosa sia per spacy che per fasttext


import os,sys,inspect
import yaml
from sklearn.preprocessing import MinMaxScaler
import pandas as pd


# cve_list=["CVE-2015-1427", "CVE-2015-4165", "CVE-2015-5531", "CVE-2019-7619", "CVE-2020-7009"]
results_spacy_list = list()
results_fasttext_list = list()

cve_list=["CVE-2015-1427", "CVE-2015-4165", "CVE-2015-5531", "CVE-2019-7619", "CVE-2020-7009", "CVE-2020-7019", "CVE-2013-4152", "CVE-2013-6429",
"CVE-2013-6430", "CVE-2013-7315", "CVE-2014-0054", "CVE-2014-0225", "CVE-2014-1904","CVE-2014-3578", "CVE-2014-3625", "CVE-2015-0201",
"CVE-2015-3192", "CVE-2016-5007", "CVE-2016-9878","CVE-2018-11039", "CVE-2018-11040", "CVE-2018-1257","CVE-2018-1270", "CVE-2018-1271",
"CVE-2018-1272", "CVE-2018-1275","CVE-2018-15756", "CVE-2020-5397", "CVE-2020-5398", "CVE-2018-10237", "CVE-2016-2402", "CVE-2018-1000844",
"CVE-2018-1000850", "CVE-2017-12612", "CVE-2020-9480", "CVE-2014-0193", "CVE-2014-3488", "CVE-2015-2156", "CVE-2016-4970", "CVE-2019-16869",
"CVE-2019-20445", "CVE-2019-9512", "CVE-2019-9514", "CVE-2019-9515", "CVE-2019-9518", "CVE-2020-11612", "CVE-2020-7238", "CVE-2017-18349",
"CVE-2017-12610", "CVE-2018-17196", "CVE-2019-12399", "CVE-2018-17297", "CVE-2020-13921", "CVE-2020-9483", "CVE-2020-1960", "CVE-2019-17572",
"CVE-2020-12480", "CVE-2014-0229", "CVE-2015-1776", "CVE-2016-5001", "CVE-2017-3166", "CVE-2017-7669", "CVE-2018-11768", "CVE-2018-8009",
"CVE-2018-12541", "CVE-2020-1958", "CVE-2018-11248", "CVE-2017-5637", "CVE-2018-8012", "CVE-2019-0201", "CVE-2016-9177", "CVE-2018-9159"]


def scaleValues(tuple_list):
  value_list = [[tuple_el[1]] for tuple_el in tuple_list]
  new_value_list = list()
  scaler = MinMaxScaler()
  scaled_values = scaler.fit_transform(value_list)

  for i, el in enumerate(tuple_list):
    new_value_list.append((el[0], scaled_values[i][0]))


  return new_value_list


for cve in cve_list:
  vulnerability_id = cve
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
       project_url = '.'.join(project_url.split('.')[:-1])
       project_name = project_name.split('.')[0]
  print(cve + " " +project_name)
  # print(project_name)

  # print(parsed_statments['fixes'])
  # print(parsed_statments['fixes'][0]['id'])

  for fix in parsed_statments['fixes']:
    # print(fix['commits'][0]['id'])
    # commit_sha = fix['commits'][0]['id']
    for com in fix['commits']:
      commit_sha = com['id']
      print(com['id'])
      os.chdir("diff_commits/"+cve)
      
      order_commits_similarity_file = open("order_commits_similarity_file.txt", "r")
      order_commits_similarity_file_list = list()
      for lines in order_commits_similarity_file.readlines():
          sha, value = lines.split(",")
          sha = sha[2:-1]
          value = value[2:-3]
          order_commits_similarity_file_list.append((sha, float(value)))
      spacy_scaled_list = scaleValues(order_commits_similarity_file_list)

      order_commits_similarity_file_fasttext = open("order_commits_similarity_file_fasttext.txt", "r")
      order_commits_similarity_file_fasttext_list = list()
      for lines in order_commits_similarity_file_fasttext.readlines():
          sha, value = lines.split(",")
          sha = sha[2:-1]
          value = value[2:-3]
          order_commits_similarity_file_fasttext_list.append((sha, float(value)))
      # print(order_commits_similarity_file_fasttext_list)
      fasttext_scaled_list = scaleValues(order_commits_similarity_file_fasttext_list)

      found = False
      for item in spacy_scaled_list:
        if item[0][:-1] == commit_sha or item[0] == commit_sha:
          similarity = item[1]
          found = True
          results_spacy_list.append((cve, project_name, project_url, commit_sha, similarity, found))
      if not found:
        results_spacy_list.append((cve, project_name, project_url, commit_sha, None, found))
      
      found = False
      for item in fasttext_scaled_list: 
        if item[0][:-1] == commit_sha or item[0] == commit_sha:
          found = True
          results_fasttext_list.append((cve, project_name, project_url, commit_sha, similarity, found))
      if not found:
        results_fasttext_list.append((cve, project_name, project_url, commit_sha, None, found))
      
      os.chdir(current_working_directory)

columns = ['cve', 'project_name', 'project_url', 'commit_sha', 'similarity', 'match']
df_spacy = pd.DataFrame(results_spacy_list, columns =columns)
df_fasttext = pd.DataFrame(results_fasttext_list, columns =columns)

df_spacy.to_csv('final_results_spacy.csv')
df_fasttext.to_csv('final_results_fasttext.csv')
