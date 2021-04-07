

# %%
import pandas as pd

import os,sys,inspect
import yaml

RECALL_AT_1 = 1
RECALL_AT_5 = 5
RECALL_AT_10 = 10
RECALL_AT_20 = 20

cve_list=["CVE-2015-1427", "CVE-2015-4165", "CVE-2015-5531", "CVE-2019-7619", "CVE-2020-7009", "CVE-2020-7019", "CVE-2013-4152", "CVE-2013-6429",
"CVE-2013-6430", "CVE-2013-7315", "CVE-2014-0054", "CVE-2014-0225", "CVE-2014-1904","CVE-2014-3578", "CVE-2014-3625", "CVE-2015-0201",
"CVE-2015-3192", "CVE-2016-5007", "CVE-2016-9878","CVE-2018-11039", "CVE-2018-11040", "CVE-2018-1257","CVE-2018-1270", "CVE-2018-1271",
"CVE-2018-1272", "CVE-2018-1275","CVE-2018-15756", "CVE-2020-5397", "CVE-2020-5398", "CVE-2018-10237", "CVE-2016-2402", "CVE-2018-1000844",
"CVE-2018-1000850", "CVE-2017-12612", "CVE-2020-9480", "CVE-2014-0193", "CVE-2014-3488", "CVE-2015-2156", "CVE-2016-4970", "CVE-2019-16869",
"CVE-2019-20445", "CVE-2019-9512", "CVE-2019-9514", "CVE-2019-9515", "CVE-2019-9518", "CVE-2020-11612", "CVE-2020-7238", "CVE-2017-18349",
"CVE-2017-12610", "CVE-2018-17196", "CVE-2019-12399", "CVE-2018-17297", "CVE-2020-13921", "CVE-2020-9483", "CVE-2020-1960", "CVE-2019-17572",
"CVE-2020-12480", "CVE-2014-0229", "CVE-2015-1776", "CVE-2016-5001", "CVE-2017-3166", "CVE-2017-7669", "CVE-2018-11768", "CVE-2018-8009",
"CVE-2018-12541", "CVE-2020-1958", "CVE-2018-11248", "CVE-2017-5637", "CVE-2018-8012", "CVE-2019-0201", "CVE-2016-9177", "CVE-2018-9159"]


fix_commits_df_spacy = pd.DataFrame(columns=['vulnerability_id', 'commit_id', 'spacy_similarity', 'rank'])
fix_commits_df_fasttext = pd.DataFrame(columns=['vulnerability_id', 'commit_id', 'fasttext_similarity', 'rank'])
spacy_df = pd.DataFrame()
fasttext_df = pd.DataFrame()

spacy_df = pd.read_csv('all_cve_similarity_ranked_spacy.csv', index_col=0)
fasttext_df = pd.read_csv('all_cve_similarity_ranked_fasttext.csv', index_col=0)

# %%
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
  # print(cve + " " +project_name)
  # print(project_name)

  # print(parsed_statments['fixes'])
  # print(parsed_statments['fixes'][0]['id'])

  for fix in parsed_statments['fixes']:
    # print(fix['commits'][0]['id'])
    # commit_sha = fix['commits'][0]['id']
    for com in fix['commits']:

      cve_df = pd.DataFrame()
      cve_df = spacy_df.loc[spacy_df['vulnerability_id'] == cve]
      # cve_df.head()
      fix_row = pd.DataFrame()
      fix_row = cve_df.loc[cve_df['commit_id'].isin([com['id']]) | cve_df['commit_id'].str.contains(com['id'])]
      fix_commits_df_spacy = pd.concat([fix_commits_df_spacy, fix_row], ignore_index=True)

      
      cve_df = pd.DataFrame()
      cve_df = fasttext_df.loc[fasttext_df['vulnerability_id'] == cve]
      # cve_df.head()
      fix_row = pd.DataFrame()
      fix_row = cve_df.loc[cve_df['commit_id'].isin([com['id']]) | cve_df['commit_id'].str.contains(com['id'])]
      fix_commits_df_fasttext = pd.concat([fix_commits_df_fasttext, fix_row], ignore_index=True)
      # fix_commits_df_spacy.append()
# %%
num_spacy_elem = len(fix_commits_df_spacy.index)
num_fasttext_elem = len(fix_commits_df_fasttext.index)

# %%
print(fix_commits_df_spacy)
# %%
print(fix_commits_df_fasttext)

# %%
fix_commits_df_fasttext.to_csv('check2_fasttext.csv') 
# %%
# fix_commits_df_spacy.to_csv('check2.csv') 
# %%
print(num_spacy_elem)
# %%
print(num_fasttext_elem)
# %%
spacy_count_recall_1 = 0
spacy_count_recall_5 = 0
spacy_count_recall_10 = 0
spacy_count_recall_20 = 0
for index, vuln_fix in fix_commits_df_spacy.iterrows():
  if vuln_fix['rank'] <= RECALL_AT_1:
    spacy_count_recall_1 += 1
  if vuln_fix['rank'] <= RECALL_AT_5:
    spacy_count_recall_5 += 1
  if vuln_fix['rank'] <= RECALL_AT_10:
    spacy_count_recall_10 += 1
  if vuln_fix['rank'] <= RECALL_AT_20:
    spacy_count_recall_20 += 1

spacy_precision_1 = (spacy_count_recall_1 * 100) / num_spacy_elem
spacy_precision_5 = (spacy_count_recall_5 * 100) / num_spacy_elem
spacy_precision_10 = (spacy_count_recall_10 * 100) / num_spacy_elem
spacy_precision_20 = (spacy_count_recall_20 * 100) / num_spacy_elem

fasttext_count_recall_1 = 0
fasttext_count_recall_5 = 0
fasttext_count_recall_10 = 0
fasttext_count_recall_20 = 0
for index, vuln_fix in fix_commits_df_fasttext.iterrows():
  if vuln_fix['rank'] <= RECALL_AT_1:
    fasttext_count_recall_1 += 1
  if vuln_fix['rank'] <= RECALL_AT_5:
    fasttext_count_recall_5 += 1
  if vuln_fix['rank'] <= RECALL_AT_10:
    fasttext_count_recall_10 += 1
  if vuln_fix['rank'] <= RECALL_AT_20:
    fasttext_count_recall_20 += 1

fasttext_precision_1 = (fasttext_count_recall_1 * 100) / num_fasttext_elem
fasttext_precision_5 = (fasttext_count_recall_5 * 100) / num_fasttext_elem
fasttext_precision_10 = (fasttext_count_recall_10 * 100) / num_fasttext_elem
fasttext_precision_20 = (fasttext_count_recall_20 * 100) / num_fasttext_elem
# %%
print(spacy_precision_5)

# %%
print(spacy_precision_10)

# %%
print(spacy_precision_20)
# %%
results_df = pd.DataFrame([['spacy', spacy_precision_1, spacy_precision_5, spacy_precision_10, spacy_precision_20], 
  ['fasttext', fasttext_precision_1, fasttext_precision_5, fasttext_precision_10, fasttext_precision_20]], columns=['similarity', 'precision_first_place', 'recall_at_5', 'recall_at_10', 'recall_at_20'])

# %%
results_df.head()
# %%
print(results_df)