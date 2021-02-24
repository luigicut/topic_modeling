from FINAL_01_create_model_multip import main as models
from FINAL_02_gather_commits_multip import main as commits
from FINAL_03_similarity_prediction import main as spacy_pred
from FINAL_04_fasttext_similarity_prediction import main as fasttext_pred
from FINAL_05_file_order import main as order
from datetime import datetime
import os
import yaml
number_of_cpus = os.cpu_count()

def main():
  # cve="CVE-2019-17572"
  cve_list = ["CVE-2018-17297", "CVE-2018-12972", "CVE-2018-11248", "CVE-2018-1000850", "CVE-2018-1000844", "CVE-2016-2402"]

  for cve in cve_list: 

    
    current_working_directory = os.getcwd()
    os.environ['GIT_CACHE'] = current_working_directory + "/GIT_CACHE"
    GIT_CACHE = os.environ['GIT_CACHE']
    statments_yaml = open(current_working_directory+"/statements/"+cve+"/statement.yaml",'r')
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



    print('staring with vunlerability: '+cve)
    startTime = datetime.now()
    print('starting time: '+str(startTime))

    models(cve, number_of_cpus=6)
    commits(cve, number_of_cpus=6)
    spacy_pred(cve)
    fasttext_pred(cve)
    order(cve, 'spacy')
    order(cve, 'fasttext')
    endTime = datetime.now()

    print('started at: '+str(startTime))
    print('finished at: '+str(endTime))

    statistics = open("statistics_"+cve+".txt","a+")
    statistics.writelines(str(cve)+"\n")
    statistics.writelines(str(startTime)+"\n")
    statistics.writelines(str(endTime)+"\n\n")
    statistics.close()

if __name__ == "__main__":
  main()
