

# %%
import pandas as pd
import random
import os,sys,inspect
import yaml

RECALL_AT_1 = 1
RECALL_AT_5 = 5
RECALL_AT_10 = 10
RECALL_AT_20 = 20
kappa = 10

#72 vulnerabilities
# cve_list=["CVE-2015-1427", "CVE-2015-4165", "CVE-2015-5531", "CVE-2019-7619", "CVE-2020-7009", "CVE-2020-7019", "CVE-2013-4152", "CVE-2013-6429",
# "CVE-2013-6430", "CVE-2013-7315", "CVE-2014-0054", "CVE-2014-0225", "CVE-2014-1904","CVE-2014-3578", "CVE-2014-3625", "CVE-2015-0201",
# "CVE-2015-3192", "CVE-2016-5007", "CVE-2016-9878","CVE-2018-11039", "CVE-2018-11040", "CVE-2018-1257","CVE-2018-1270", "CVE-2018-1271",
# "CVE-2018-1272", "CVE-2018-1275","CVE-2018-15756", "CVE-2020-5397", "CVE-2020-5398", "CVE-2018-10237", "CVE-2016-2402", "CVE-2018-1000844",
# "CVE-2018-1000850", "CVE-2017-12612", "CVE-2020-9480", "CVE-2014-0193", "CVE-2014-3488", "CVE-2015-2156", "CVE-2016-4970", "CVE-2019-16869",
# "CVE-2019-20445", "CVE-2019-9512", "CVE-2019-9514", "CVE-2019-9515", "CVE-2019-9518", "CVE-2020-11612", "CVE-2020-7238", "CVE-2017-18349",
# "CVE-2017-12610", "CVE-2018-17196", "CVE-2019-12399", "CVE-2018-17297", "CVE-2020-13921", "CVE-2020-9483", "CVE-2020-1960", "CVE-2019-17572",
# "CVE-2020-12480", "CVE-2014-0229", "CVE-2015-1776", "CVE-2016-5001", "CVE-2017-3166", "CVE-2017-7669", "CVE-2018-11768", "CVE-2018-8009",
# "CVE-2018-12541", "CVE-2020-1958", "CVE-2018-11248", "CVE-2017-5637", "CVE-2018-8012", "CVE-2019-0201", "CVE-2016-9177", "CVE-2018-9159"]

#63 vulnerabilities
cve_list=["CVE-2015-1427", "CVE-2015-5531", "CVE-2019-7619", "CVE-2020-7009", "CVE-2020-7019", "CVE-2013-4152", "CVE-2013-6429",
"CVE-2013-7315", "CVE-2014-0054", "CVE-2014-1904","CVE-2014-3578", "CVE-2014-3625", "CVE-2015-0201",
"CVE-2015-3192", "CVE-2016-5007", "CVE-2016-9878","CVE-2018-11039", "CVE-2018-11040", "CVE-2018-1257","CVE-2018-1270", "CVE-2018-1271",
"CVE-2018-1272", "CVE-2018-1275","CVE-2018-15756", "CVE-2020-5397", "CVE-2020-5398", "CVE-2018-10237", "CVE-2016-2402", "CVE-2018-1000844",
"CVE-2018-1000850", "CVE-2017-12612", "CVE-2020-9480", "CVE-2014-0193", "CVE-2014-3488", "CVE-2016-4970", "CVE-2019-16869",
"CVE-2019-20445", "CVE-2019-9512", "CVE-2019-9514", "CVE-2019-9515", "CVE-2019-9518", "CVE-2020-11612", "CVE-2020-7238", "CVE-2017-18349",
"CVE-2017-12610", "CVE-2018-17196", "CVE-2019-12399", "CVE-2018-17297", "CVE-2020-13921", "CVE-2020-9483", "CVE-2020-1960", "CVE-2019-17572",
"CVE-2020-12480", "CVE-2017-7669", "CVE-2018-11768", "CVE-2018-8009",
"CVE-2018-12541", "CVE-2020-1958", "CVE-2018-11248", "CVE-2017-5637", "CVE-2019-0201", "CVE-2016-9177", "CVE-2018-9159"]
# cve_list= ["CVE-2016-9177","CVE-2018-9159"]


spacy_df = pd.DataFrame()
fasttext_df = pd.DataFrame()
results_df = pd.DataFrame(columns=['try_n', 'vulnerability_id', 'fix_commit_mean_sim', 'not_fix_commit_mean_sim', 'num_fix_commit', 'type'])
spacy_df = pd.read_csv('all_cve_similarity_ranked_spacy.csv', index_col=0)
fasttext_df = pd.read_csv('all_cve_similarity_ranked_fasttext.csv', index_col=0)

# %%
for iteration in range(10):
  print(iteration)
  fix_commits_df_spacy = pd.DataFrame(columns=['try_n', 'vulnerability_id', 'commit_id', 'spacy_similarity', 'rank'])
  fix_commits_df_fasttext = pd.DataFrame(columns=['try_n', 'vulnerability_id', 'commit_id', 'fasttext_similarity', 'rank'])
  not_fix_commits_df_spacy = pd.DataFrame(columns=['try_n', 'vulnerability_id', 'commit_id', 'spacy_similarity', 'rank'])
  not_fix_commits_df_fasttext = pd.DataFrame(columns=['try_n', 'vulnerability_id', 'commit_id', 'fasttext_similarity', 'rank'])

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
    fix_commits_for_cve = list()
    cve_df_spacy = pd.DataFrame()
    cve_df_spacy = spacy_df.loc[spacy_df['vulnerability_id'] == cve]
    cve_df_spacy['try_n'] = iteration
    cve_df_fasttext = pd.DataFrame()
    cve_df_fasttext = fasttext_df.loc[fasttext_df['vulnerability_id'] == cve]
    cve_df_fasttext['try_n'] = iteration

    # print(cve_df_spacy)

    for fix in parsed_statments['fixes']:
      # print(fix['commits'][0]['id'])
      # commit_sha = fix['commits'][0]['id']
      for com in fix['commits']:

        fix_commits_for_cve.append(com['id'])
      # print(len(fix_commits_for_cve))

      not_fix_row_spacy = pd.DataFrame()
      # print(len(cve_df_spacy))
      cve_df_spacy_without_fix_commits = pd.DataFrame()
      cve_df_spacy_without_fix_commits = cve_df_spacy[-cve_df_spacy['commit_id'].isin(fix_commits_for_cve)]  
      # print(len(cve_df_spacy))

      not_fix_row_spacy = cve_df_spacy_without_fix_commits.sample(n=len(fix_commits_for_cve)*kappa)
      not_fix_commits_df_spacy = pd.concat([not_fix_commits_df_spacy, not_fix_row_spacy], ignore_index=True)
      # print(len(not_fix_row_spacy))
      # print(len(not_fix_commits_df_spacy))

      not_fix_row_fasttext = pd.DataFrame()
      cve_df_fasttext_without_fix_commits = pd.DataFrame()
      cve_df_fasttext_without_fix_commits = cve_df_fasttext[-cve_df_fasttext['commit_id'].isin(fix_commits_for_cve)] 

      not_fix_row_fasttext = cve_df_fasttext_without_fix_commits.sample(n=len(fix_commits_for_cve)*kappa)
      not_fix_commits_df_fasttext = pd.concat([not_fix_commits_df_fasttext, not_fix_row_fasttext], ignore_index=True)
      # print(len(not_fix_row_fasttext))
      # print(len(not_fix_commits_df_fasttext))

      for com in fix['commits']:

        # fix_commits_for_cve.append(com['id'])
        fix_row = pd.DataFrame()
        fix_row = cve_df_spacy.loc[cve_df_spacy['commit_id'].isin([com['id']]) | cve_df_spacy['commit_id'].str.contains(com['id'])]
        fix_commits_df_spacy = pd.concat([fix_commits_df_spacy, fix_row], ignore_index=True)
        # not_fix_row = pd.DataFrame()
        # not_fix_row = cve_df_spacy.loc[cve_df_spacy['commit_id'].isin([com['id']]) | cve_df_spacy['commit_id'].str.contains(com['id'])]
        # not_fix_commits_df_spacy = pd.concat([fix_commits_df_spacy, fix_row], ignore_index=True)
        
      # for com in fix_commits_for_cve:
        # cve_df.head()


        # fix_commits_df_spacy = pd.concat([fix_commits_df_spacy, fix_row], ignore_index=True)

        

        # cve_df.head()
        fix_row = pd.DataFrame()
        fix_row = cve_df_fasttext.loc[cve_df_fasttext['commit_id'].isin([com['id']]) | cve_df_fasttext['commit_id'].str.contains(com['id'])]
        fix_commits_df_fasttext = pd.concat([fix_commits_df_fasttext, fix_row], ignore_index=True)
        # fix_commits_df_spacy.append()


  # # %%
  # fix_commits_df_spacy.head()
  # # %%
  # fix_commits_df_fasttext.head()
  # # %%
  # not_fix_commits_df_spacy.head()
  # # %%
  # not_fix_commits_df_fasttext.head()
  # # %%

  # temp_df = pd.DataFrame()
  # temp_df = fix_commits_df_spacy.loc[fix_commits_df_spacy['vulnerability_id'] == cve]
  # num_fix_commit = len(temp_df)
  # fix_commit_mean_sim_spacy = temp_df["spacy_similarity"].mean()
  # temp_df = not_fix_commits_df_spacy.loc[not_fix_commits_df_spacy['vulnerability_id'] == cve]
  # not_fix_commit_mean_sim_spacy = temp_df["spacy_similarity"].mean()
  # temp_df = fix_commits_df_fasttext.loc[fix_commits_df_fasttext['vulnerability_id'] == cve]
  # fix_commit_mean_sim_fasttext = temp_df["fasttext_similarity"].mean()
  # temp_df = not_fix_commits_df_fasttext.loc[not_fix_commits_df_fasttext['vulnerability_id'] == cve]
  # not_fix_commit_mean_sim_fasttext = temp_df["fasttext_similarity"].mean()


  for cve in cve_list:
    temp_df = pd.DataFrame()
    temp_df = fix_commits_df_spacy.loc[fix_commits_df_spacy['vulnerability_id'] == cve]
    num_fix_commit = len(temp_df)
    fix_commit_mean_sim_spacy = temp_df["spacy_similarity"].mean()
    temp_df = not_fix_commits_df_spacy.loc[not_fix_commits_df_spacy['vulnerability_id'] == cve]
    not_fix_commit_mean_sim_spacy = temp_df["spacy_similarity"].mean()
    temp_df = fix_commits_df_fasttext.loc[fix_commits_df_fasttext['vulnerability_id'] == cve]
    fix_commit_mean_sim_fasttext = temp_df["fasttext_similarity"].mean()
    temp_df = not_fix_commits_df_fasttext.loc[not_fix_commits_df_fasttext['vulnerability_id'] == cve]
    not_fix_commit_mean_sim_fasttext = temp_df["fasttext_similarity"].mean()
    # results_df.append({cve, fix_commit_mean_sim_spacy, not_fix_commit_mean_sim_spacy, num_fix_commit, 'spacy'})
    results_df = results_df.append({'try_n': iteration, 'vulnerability_id': cve, 'fix_commit_mean_sim': fix_commit_mean_sim_spacy, 'not_fix_commit_mean_sim': not_fix_commit_mean_sim_spacy, 'num_fix_commit': num_fix_commit, 'type': 'spacy'}, ignore_index=True)
    results_df = results_df.append({'try_n': iteration, 'vulnerability_id': cve, 'fix_commit_mean_sim': fix_commit_mean_sim_fasttext, 'not_fix_commit_mean_sim': not_fix_commit_mean_sim_fasttext, 'num_fix_commit': num_fix_commit, 'type': 'fasttext'}, ignore_index=True)
  results_df.head()


print(results_df)

# # %%
results_df.to_csv('compare_similarities.csv')

# %%



# media di tutti i valori e compare

# contare quanti valori di medi di similarity di fix commit per cve sono più alti di dei valori medi di similarity dei non fix commit 
#la tabella puàò contenere2 right, una per spacy e una per fasttext
# colonne : type, fix_commit_sim_gt_not_fix_commit_sim, not_fix_commit_sim_gt_fix_commit_sim

compare_count_sim = pd.DataFrame(columns=['try_n', 'type', 'fix_commit_sim_gt_not_fix_commit_sim', 'not_fix_commit_sim_gt_fix_commit_sim', 'similarity_mean_diff'])
   
for iteration in range(10):
  spacy_rows = results_df[(results_df['type'] == 'spacy') & (results_df['try_n'] == iteration)]
  fasttext_rows = results_df[(results_df['type'] == 'fasttext') & (results_df['try_n'] == iteration)]   
  fix_commit_sim_gt_not_fix_commit_sim_spacy = 0
  fix_commit_sim_gt_not_fix_commit_sim_fasttext = 0
  worst_spacy_not_win = 0
  worst_spacy_fix_win = 100
  for index, spacy_row in spacy_rows.iterrows():
    if spacy_row['fix_commit_mean_sim'] > spacy_row['not_fix_commit_mean_sim']:
      fix_commit_sim_gt_not_fix_commit_sim_spacy += 1
      if worst_spacy_fix_win > (spacy_row['fix_commit_mean_sim'] - spacy_row['not_fix_commit_mean_sim']):
        worst_spacy_fix_win = spacy_row['fix_commit_mean_sim'] - spacy_row['not_fix_commit_mean_sim']
    else:
      if worst_spacy_not_win < (spacy_row['not_fix_commit_mean_sim'] - spacy_row['fix_commit_mean_sim']):
        worst_spacy_not_win = spacy_row['not_fix_commit_mean_sim'] - spacy_row['fix_commit_mean_sim']
  worst_fasttext_not_win = 0
  worst_fasttext_fix_win = 100
  for index, fasttext_row in fasttext_rows.iterrows():
    if fasttext_row['fix_commit_mean_sim'] > fasttext_row['not_fix_commit_mean_sim']:
      fix_commit_sim_gt_not_fix_commit_sim_fasttext += 1
      if worst_fasttext_fix_win > (fasttext_row['fix_commit_mean_sim'] - fasttext_row['not_fix_commit_mean_sim']):
        worst_fasttext_fix_win = fasttext_row['fix_commit_mean_sim'] - fasttext_row['not_fix_commit_mean_sim']
    else:
      if worst_fasttext_not_win < (fasttext_row['not_fix_commit_mean_sim'] - fasttext_row['fix_commit_mean_sim']):
        worst_fasttext_not_win = fasttext_row['not_fix_commit_mean_sim'] - fasttext_row['fix_commit_mean_sim']

  similarity_mean_diff_spacy = 0
  if (worst_spacy_not_win > 0):
    similarity_mean_diff_spacy = 0 - worst_spacy_not_win
  else:
    similarity_mean_diff_spacy = worst_spacy_fix_win

  similarity_mean_diff_fasttext = 0
  if (worst_fasttext_not_win > 0):
    similarity_mean_diff_fasttext = 0 - worst_fasttext_not_win
  else:
    similarity_mean_diff_fasttext = worst_fasttext_fix_win


  compare_count_sim = compare_count_sim.append({'try_n': iteration, 'type': 'spacy', 'fix_commit_sim_gt_not_fix_commit_sim': fix_commit_sim_gt_not_fix_commit_sim_spacy, 'not_fix_commit_sim_gt_fix_commit_sim': len(spacy_rows) - fix_commit_sim_gt_not_fix_commit_sim_spacy, 'similarity_mean_diff': similarity_mean_diff_spacy}, ignore_index=True)
  compare_count_sim = compare_count_sim.append({'try_n': iteration, 'type': 'fasttext', 'fix_commit_sim_gt_not_fix_commit_sim': fix_commit_sim_gt_not_fix_commit_sim_fasttext, 'not_fix_commit_sim_gt_fix_commit_sim': len(spacy_rows) - fix_commit_sim_gt_not_fix_commit_sim_fasttext, 'similarity_mean_diff': similarity_mean_diff_fasttext}, ignore_index=True)
  # ([['spacy', fix_commit_sim_gt_not_fix_commit_sim_spacy, len(spacy_rows) - fix_commit_sim_gt_not_fix_commit_sim_spacy], 
    # ['fasttext', fix_commit_sim_gt_not_fix_commit_sim_fasttext, len(fasttext_rows) - fix_commit_sim_gt_not_fix_commit_sim_fasttext]], columns=['type', 'fix_commit_sim_gt_not_fix_commit_sim', 'not_fix_commit_sim_gt_fix_commit_sim'])

def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    if(not isinstance(val, str)):
      color = 'red' if val < 0 else ''
      return 'color: %s' % color
    return val

s = compare_count_sim.style.applymap(color_negative_red)
s
# compare_count_sim.head(20)


# %%
compare_mean_sim = pd.DataFrame(columns=['try_n', 'type', 'sim_mean_fix_commit', 'sim_mean_not_fix_commit'])
for iteration in range(10):
  spacy_rows = results_df[(results_df['type'] == 'spacy') & (results_df['try_n'] == iteration)]
  fasttext_rows = results_df[(results_df['type'] == 'fasttext') & (results_df['try_n'] == iteration)]   
  fix_commit_sim_gt_not_fix_commit_sim_spacy = 0
  fix_commit_sim_gt_not_fix_commit_sim_fasttext = 0
  for index, spacy_row in spacy_rows.iterrows():
    if spacy_row['fix_commit_mean_sim'] > spacy_row['not_fix_commit_mean_sim']:
      fix_commit_sim_gt_not_fix_commit_sim_spacy += 1

  for index, fasttext_row in fasttext_rows.iterrows():
    if fasttext_row['fix_commit_mean_sim'] > fasttext_row['not_fix_commit_mean_sim']:
      fix_commit_sim_gt_not_fix_commit_sim_fasttext += 1

  compare_mean_sim = compare_mean_sim.append({'try_n': iteration, 'type': 'spacy', 'sim_mean_fix_commit': spacy_rows["fix_commit_mean_sim"].mean(), 'sim_mean_not_fix_commit': spacy_rows["not_fix_commit_mean_sim"].mean()}, ignore_index=True)
  compare_mean_sim = compare_mean_sim.append({'try_n': iteration, 'type': 'fasttext', 'sim_mean_fix_commit': fasttext_rows["fix_commit_mean_sim"].mean(), 'sim_mean_not_fix_commit': fasttext_rows["not_fix_commit_mean_sim"].mean()}, ignore_index=True)
    # [['spacy', spacy_rows["fix_commit_mean_sim"].mean(), spacy_rows["not_fix_commit_mean_sim"].mean()], 
    # ['fasttext', fasttext_rows["fix_commit_mean_sim"].mean(), fasttext_rows["not_fix_commit_mean_sim"].mean()]], columns=['type', 'sim_mean_fix_commit', 'sim_mean_not_fix_commit'])
compare_mean_sim.head(20)



# %%
cve_df_spacy.head()