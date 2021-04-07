


import gather_commits
import os, ast
import yaml
import chardet
from core import Git, Commit
from tqdm import tqdm

current_working_directory = os.getcwd()
GIT_CACHE = current_working_directory + "/GIT_CACHE"
from multiprocessing import Pool

# cve_list= list()

cve_dict = {
  # "vert.x":["CVE-2018-12541"],
  # "druid":["CVE-2020-1958"],
  # "kafka": ["CVE-2017-12610", "CVE-2018-17196", "CVE-2019-12399"],
  # "skywalking": ["CVE-2020-13921", "CVE-2020-9483"],
  # "elasticsearch": ["CVE-2015-1427", "CVE-2015-4165", "CVE-2015-5531", "CVE-2019-7619", "CVE-2020-7009", "CVE-2020-7019"],
  # "spring-framework": ["CVE-2013-4152", "CVE-2013-6429", "CVE-2013-6430",
  #   "CVE-2013-7315", "CVE-2014-0054", "CVE-2014-0225", "CVE-2014-1904",
  #   "CVE-2014-3578", "CVE-2014-3625", "CVE-2015-0201", "CVE-2015-3192",
  #   "CVE-2016-5007", "CVE-2016-9878", "CVE-2018-11039", "CVE-2018-11040",
  #   "CVE-2018-1257", "CVE-2018-1270", "CVE-2018-1271", "CVE-2018-1272",
  #   "CVE-2018-1275", "CVE-2018-15756", "CVE-2020-5397", "CVE-2020-5398"],
  # "guava": ["CVE-2018-10237"], 
  # "okhttp":["CVE-2016-2402"],
  # "retrofit": ["CVE-2018-1000844", "CVE-2018-1000850"],
  # "spark": ["CVE-2017-12612", "CVE-2020-9480"], 
  # "netty": ["CVE-2014-0193","CVE-2014-3488","CVE-2015-2156", "CVE-2016-4970", "CVE-2019-16869", "CVE-2019-20445",
  #   "CVE-2019-9512","CVE-2019-9514", "CVE-2019-9515", "CVE-2019-9518","CVE-2020-11612", "CVE-2020-7238"],
  # "fastjson": ["CVE-2017-18349"], 
  # "hutool": ["CVE-2018-17297"],
  # "flink": ["CVE-2020-1960"],
  # "rocketmq": ["CVE-2019-17572"],
  # "playframework": ["CVE-2020-12480"],
  # "hadoop":["CVE-2014-0229", "CVE-2015-1776", "CVE-2016-5001", "CVE-2017-3166", "CVE-2017-7669", "CVE-2018-11768", "CVE-2018-8009"],
  # "FileDownloader":["CVE-2018-11248"],
  # "zookeeper": ["CVE-2017-5637","CVE-2018-8012", "CVE-2019-0201"],
  "perwendel-spark":["CVE-2016-9177", "CVE-2018-9159"]
}

# cve_list = [
# "CVE-2015-1427", "CVE-2015-4165", "CVE-2015-5531", "CVE-2019-7619", "CVE-2020-7009",
# "CVE-2020-7019", "CVE-2013-4152", "CVE-2013-6429", "CVE-2013-6430",
# "CVE-2013-7315", "CVE-2014-0054", "CVE-2014-0225", "CVE-2014-1904",
# "CVE-2014-3578", "CVE-2014-3625", "CVE-2015-0201", "CVE-2015-3192",
# "CVE-2016-5007", "CVE-2016-9878", "CVE-2018-11039", "CVE-2018-11040",
# "CVE-2018-1257", "CVE-2018-1270", "CVE-2018-1271", "CVE-2018-1272",
# "CVE-2018-1275", "CVE-2018-15756", "CVE-2020-5397", "CVE-2020-5398",
# "CVE-2018-10237", "CVE-2016-2402", "CVE-2018-1000844", "CVE-2018-1000850",
# "CVE-2017-12612", "CVE-2020-9480", "CVE-2014-0193","CVE-2014-3488",
# "CVE-2015-2156", "CVE-2016-4970", "CVE-2019-16869", "CVE-2019-20445",
# "CVE-2019-9512","CVE-2019-9514", "CVE-2019-9515", "CVE-2019-9518",
# "CVE-2020-11612", "CVE-2020-7238", "CVE-2017-18349", "CVE-2017-12610", 
# "CVE-2018-17196", "CVE-2019-12399", "CVE-2018-17297",
# "CVE-2020-13921", "CVE-2020-9483", "CVE-2020-1960","CVE-2019-17572",
# "CVE-2020-12480", "CVE-2014-0229", "CVE-2015-1776", "CVE-2016-5001",
# "CVE-2017-3166", "CVE-2017-7669", "CVE-2018-11768", "CVE-2018-8009",
# "CVE-2018-12541", "CVE-2020-1958", "CVE-2018-11248", "CVE-2017-5637",
# "CVE-2018-8012", "CVE-2019-0201", "CVE-2016-9177", "CVE-2018-9159"]
# CVE-2018-8012 questa ha i pdf che escono danneggiati


def get_msg(project_url, commit_sha):
  git_repo = Git(project_url, cache_path=GIT_CACHE)
  git_repo.clone(skip_existing=True)
  try:
    commit = Commit(git_repo, commit_sha)
    return commit._exec.run(['git', 'log', '--format=%B', '-n1', commit._id])
  except:
    return False


def get_diff(project_url, commit_sha):
  git_repo = Git(project_url, cache_path=GIT_CACHE)
  git_repo.clone(skip_existing=True)
  try:
    commit = Commit(git_repo, commit_sha)
    return commit._exec.run(['git', 'diff', '--unified=1', commit._id + "^.." + commit._id])
  except:
    return False


def check_commit(project_url, commit_sha):
  MAX_FILE_NUMBER = 20
  # git_repo = Git(project_url, cache_path=GIT_CACHE)
  # git_repo.clone(skip_existing=True)
  
  try:
    # commit = Commit(git_repo, commit_sha)
    diff = get_diff(project_url, commit_sha)
    if type(diff) == str:
      diff = ast.literal_eval(diff)
    else:
      return 'continue'
    paths_list= list()
    for i in range(0, len(diff)):
      if (diff[i].startswith('diff --git ')):
        if not diff[i+1].startswith('deleted') and not diff[i+1].startswith('similarity'):
          path = diff[i].split(' b/')[1].rstrip("\n")
          paths_list.append(path)
    file_counter = 0
    for path in paths_list: 
      file_name = path.split('/')[-1].rstrip("\n")
      file_type = file_name.split('.')[-1]
      if file_type == 'java':
        file_counter += 1

    if(file_counter > 0 and file_counter <= MAX_FILE_NUMBER):
      return True
    else:
      return False
  except:
    return 'continue'

def count_commits_per_project(cve_dict, proj_name):
  cve_list = cve_dict[proj_name]
  results= {}
  for cve in cve_list:
    
    vulnerability_id = cve
    
    statments_yaml = open(current_working_directory+"/statements/"+vulnerability_id+"/statement.yaml",'r')
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
    print(project_name+" "+vulnerability_id)

    commit_list = list()
    commit_list = gather_commits.get_commit_list(vulnerability_id, project_url)
    

    filtered_commit_list = list()
    for commit in tqdm(commit_list):
      result = check_commit(project_url, commit)
      if(result == 'continue'):
        continue
      if result:
        filtered_commit_list.append(commit)



    print("effective commits per cve: "+str(len(filtered_commit_list)))
    if not results.get(project_name):
      results[project_name] = list()
    for commit in filtered_commit_list:
      if commit not in results[project_name]:
        results[project_name].append(commit)

    print("effective commits per project: "+str(len(results[project_name])))

  results_report_file = open("results_"+project_name+".txt","a+")
  for key in results.keys():
    results_report_file.writelines(key+" :"+str(len(results[key]))+" commits\n")

  results_report_file.close()

def main():
  print(cve_dict.keys())
  # input_list = [(commit, current_working_directory, project_name, vulnerability_id, project_url) for commit in commit_list]
  input_list = [(cve_dict, proj_name) for proj_name in cve_dict.keys()]
  with Pool(6) as p:
    p.starmap(count_commits_per_project, input_list)

if __name__ == "__main__":
  main()



     