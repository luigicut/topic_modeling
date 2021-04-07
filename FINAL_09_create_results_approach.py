
#per ogni CVE, prendere i commit rilevati negli statements
  #per ogni commit rilevato, cercare nel file delle prediction ordinate (il file delle
  # prediction ordinate deve diventare una lista di tuple), quel commit
  # prendere il valore di similarità di quel commit

  #normalizzare il valore di similarità di quel commit basandosi sul massimo valore sul file della prediction 
  # salvare in un file di RESULTS una row con la CVE, il commit e il valore di similarity normalizzato
  #fare la stessa cosa sia per spacy che per fasttext


# in pratica quello che devo fare è prendere le prediction di ogni CVE considerata e vedere dove
#  si posizione il fix commit di project KB per farlo devo in qualche modo aggregare i commit 
# che sono assimilabili come uguali, ma che vengono semplicemente mergiati in diversi branch.
#  secondo me il nome dei file che toccano non basta, forse dovremmo andare a leggere pure le
#  linee che modificano dal commit diff. 
# Su ogni commit controlliamo il diff, così vediamo quali file modifica, e sempre nel diff 
# vediamo se per quei file uguali, anche le linee modificate sono uguali



import os,sys,inspect
import yaml
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
# from core import Git, Commit
import utils
from tqdm import tqdm

# order_commits_similarity_file_list = list()
# order_commits_similarity_file_fasttext_list = list()
ranked_spacy_scaled_list = list()
ranked_fasttext_scaled_list = list()

# cve_list=["CVE-2015-1427", "CVE-2015-4165", "CVE-2015-5531", "CVE-2019-7619", "CVE-2020-7009"]
# results_spacy_list = list()
# results_fasttext_list = list()
#ALL CVEs
cve_list=["CVE-2015-1427", "CVE-2015-4165", "CVE-2015-5531", "CVE-2019-7619", "CVE-2020-7009", "CVE-2020-7019", "CVE-2013-4152", "CVE-2013-6429",
"CVE-2013-6430", "CVE-2013-7315", "CVE-2014-0054", "CVE-2014-0225", "CVE-2014-1904","CVE-2014-3578", "CVE-2014-3625", "CVE-2015-0201",
"CVE-2015-3192", "CVE-2016-5007", "CVE-2016-9878","CVE-2018-11039", "CVE-2018-11040", "CVE-2018-1257","CVE-2018-1270", "CVE-2018-1271",
"CVE-2018-1272", "CVE-2018-1275","CVE-2018-15756", "CVE-2020-5397", "CVE-2020-5398", "CVE-2018-10237", "CVE-2016-2402", "CVE-2018-1000844",
"CVE-2018-1000850", "CVE-2017-12612", "CVE-2020-9480", "CVE-2014-0193", "CVE-2014-3488", "CVE-2015-2156", "CVE-2016-4970", "CVE-2019-16869",
"CVE-2019-20445", "CVE-2019-9512", "CVE-2019-9514", "CVE-2019-9515", "CVE-2019-9518", "CVE-2020-11612", "CVE-2020-7238", "CVE-2017-18349",
"CVE-2017-12610", "CVE-2018-17196", "CVE-2019-12399", "CVE-2018-17297", "CVE-2020-13921", "CVE-2020-9483", "CVE-2020-1960", "CVE-2019-17572",
"CVE-2020-12480", "CVE-2014-0229", "CVE-2015-1776", "CVE-2016-5001", "CVE-2017-3166", "CVE-2017-7669", "CVE-2018-11768", "CVE-2018-8009",
"CVE-2018-12541", "CVE-2020-1958", "CVE-2018-11248", "CVE-2017-5637", "CVE-2018-8012", "CVE-2019-0201", "CVE-2016-9177", "CVE-2018-9159"]

# cve_list=["CVE-2015-1427", "CVE-2015-4165"]

def scaleValues(tuple_list):
  value_list = [[tuple_el[1]] for tuple_el in tuple_list]
  new_value_list = list()
  scaler = MinMaxScaler()
  scaled_values = scaler.fit_transform(value_list)

  for i, el in enumerate(tuple_list):
    new_value_list.append((el[0], scaled_values[i][0]))


  return new_value_list

def set_rank_considering_equal_commit_msg(spacy_scaled_list):
  global_spacy_similarity = 0.
  global_rank = 0
  global_commit_message = ''
  ranked_scaled_list = list()
  for item in tqdm(spacy_scaled_list):
    similarity = item[1]
    commit_sha = item[0]
    rank = 0
    commit_msg = utils.get_msg(project_url, commit_sha)[0]
    if similarity == global_spacy_similarity:
      if not commit_msg == '' and commit_msg == global_commit_message:
        rank = global_rank
      else:
        global_rank += 1
        rank = global_rank
    else:
      global_rank += 1
      rank = global_rank
    global_commit_message = commit_msg
    global_spacy_similarity = similarity
    ranked_scaled_list.append((cve, commit_sha, similarity, rank))
  return ranked_scaled_list




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

  os.chdir("diff_commits/"+cve)


  order_commits_similarity_file = open("order_commits_similarity_file.txt", "r")
  order_commits_similarity_file_list = list()
  for lines in order_commits_similarity_file.readlines():
      sha, value = lines.split(",")
      sha = sha[2:-1]
      value = value[2:-3]
      if value == '-1.0':
        value = '0'
      order_commits_similarity_file_list.append((sha, float(value)))
  spacy_scaled_list = scaleValues(order_commits_similarity_file_list)

  order_commits_similarity_file_fasttext = open("order_commits_similarity_file_fasttext.txt", "r")
  order_commits_similarity_file_fasttext_list = list()
  for lines in order_commits_similarity_file_fasttext.readlines():
      sha, value = lines.split(",")
      sha = sha[2:-1]
      value = value[2:-3]
      if value == '-1.0':
        value = '0'
      order_commits_similarity_file_fasttext_list.append((sha, float(value)))

  fasttext_scaled_list = scaleValues(order_commits_similarity_file_fasttext_list)

  ranked_spacy_scaled_list = ranked_spacy_scaled_list + set_rank_considering_equal_commit_msg(spacy_scaled_list)
  ranked_fasttext_scaled_list = ranked_fasttext_scaled_list + set_rank_considering_equal_commit_msg(fasttext_scaled_list)

  os.chdir(current_working_directory)

columns = ['vulnerability_id', 'commit_id', 'spacy_similarity', 'rank']
df_all_commits = pd.DataFrame(ranked_spacy_scaled_list, columns =columns)
df_all_commits.to_csv('all_cve_similarity_ranked_spacy_outliers.csv')

columns = ['vulnerability_id', 'commit_id', 'fasttext_similarity', 'rank']
df_all_commits = pd.DataFrame(ranked_fasttext_scaled_list, columns =columns)
df_all_commits.to_csv('all_cve_similarity_ranked_fasttext_outliers.csv')

    temp_df = pd.DataFrame()
    temp_df = cve_df_spacy.loc[~cve_df_spacy['commit_id'].isin(fix_commits_for_cve)]
    not_fix_row_spacy = pd.DataFrame()
    not_fix_row_spacy = temp_df.sample(n=len(fix_commits_for_cve))
    not_fix_commits_df_spacy = pd.concat([not_fix_commits_df_spacy, not_fix_row_spacy], ignore_index=True)

    temp_df = pd.DataFrame()
    temp_df = cve_df_fasttext.loc[~cve_df_fasttext['commit_id'].isin(fix_commits_for_cve)]
    not_fix_row_fasttext = pd.DataFrame()
    not_fix_row_fasttext = cve_df_fasttext.sample(n=len(fix_commits_for_cve))
    not_fix_commits_df_fasttext = pd.concat([not_fix_commits_df_fasttext, not_fix_row_fasttext], ignore_index=True)
