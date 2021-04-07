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
  # cve_list = ["CVE-2018-17297", "CVE-2018-12972", "CVE-2018-11248", "CVE-2018-1000850", "CVE-2018-1000844", "CVE-2016-2402"]
  # "CVE-2017-12612", "CVE-2020-9480", "CVE-2014-0193", "CVE-2014-3488",
#   "CVE-2015-2156", "CVE-2016-4970", "CVE-2019-16869", "CVE-2019-20445",
# "CVE-2019-9512", "CVE-2019-9514", "CVE-2019-9515", "CVE-2019-9518", "CVE-2020-11612"
    # "CVE-2020-7238", "CVE-2017-18349", "CVE-2017-12610", "CVE-2018-17196", "CVE-2019-12399", "CVE-2013-4152", "CVE-2014-0229"
    # "CVE-2020-13921", "CVE-2020-9483", "CVE-2020-1960", "CVE-2020-12480"
    # "CVE-2018-12541", "CVE-2020-1958", "CVE-2016-9177", "CVE-2018-9159"


#   cve_list = ["CVE-2015-4165", "CVE-2015-5531", "CVE-2019-7619", "CVE-2020-7009",
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
# "CVE-2020-12480", "CVE-2015-1776", "CVE-2016-5001",
# "CVE-2017-3166", "CVE-2017-7669", "CVE-2018-11768", "CVE-2018-8009",
# "CVE-2018-12541", "CVE-2020-1958", "CVE-2018-11248", "CVE-2017-5637",
# "CVE-2018-8012", "CVE-2019-0201", "CVE-2016-9177", "CVE-2018-9159"]

  # cve_list = ["CVE-2015-2156", "CVE-2014-0225", "CVE-2013-6430", "CVE-2015-4165", "CVE-2014-0229", "CVE-2015-1776", "CVE-2016-5001", "CVE-2017-3166", "CVE-2018-8012"]
  # rifatte cve_list = ["CVE-2016-9177", "CVE-2013-4152"]
  # rifatte cve_list = ["CVE-2015-1427", "CVE-2019-7619"]
  # rifatte cve_list = ["CVE-2020-7009", "CVE-2013-7315"]
  # rifatte cve_list = ["CVE-2014-0054", "CVE-2014-1904", "CVE-2014-3578"]
  # rifatte cve_list = ["CVE-2014-3625", "CVE-2018-1272", "CVE-2018-8009", "CVE-2019-0201", "CVE-2017-12610", "CVE-2019-12399", "CVE-2016-9878"]
  # cve_list = ["CVE-2015-0201", "CVE-2018-11040", "CVE-2018-1271", "CVE-2018-15756"]
  # cve_list = ["CVE-2015-3192", "CVE-2016-5007", "CVE-2018-10237", "CVE-2020-5398", "CVE-2016-2402", "CVE-2018-1000850", "CVE-2019-16869"]
  # cve_list = ["CVE-2019-20445", "CVE-2019-9512", "CVE-2019-9514", "CVE-2019-9515", "CVE-2019-9518", "CVE-2020-11612", "CVE-2017-18349", "CVE-2020-9483", "CVE-2019-17572", "CVE-2018-11768", "CVE-2018-12541", "CVE-2020-1958"]

  cve_list= ["CVE-2018-11768"]

# TODO:QUESTA NOOOO "CVE-2015-1427"  "CVE-2014-0229",

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

    # models(cve, number_of_cpus=5)
    # commits(cve, number_of_cpus=5)
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
