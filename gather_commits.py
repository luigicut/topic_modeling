#%%
import os, sys, re, difflib, spacy, ast, requests, json
import yaml
import utils
import time
from datetime import datetime

#%%
# we need "since" "until" "published_timestamp" "git_repo" ""
nist_nvd_request_url = "https://services.nvd.nist.gov/rest/json/cve/1.0/"
vulnerability_id ="CVE-2020-1961"
r = requests.get(nist_nvd_request_url+vulnerability_id)
assert r.ok == True, "vulnerability ID {} is not in the NVD".format(vulnerability_id)
cve_content = r.json()
time = cve_content['result']['CVE_Items'][0]['publishedDate'].split('T')[0]
date = datetime.datetime.strptime(time, '%Y-%m-%d')
timestamp = str((date - datetime.datetime(1970, 1, 1)).total_seconds()*1000)
print(timestamp[:-2])
published_timestamp = int(date.mktime(datetime.datetime.strptime(timestamp[:-2]).timetuple()))
# published_timestamp = int(time.mktime(datetime.datetime.strptime(cve_content['result']['CVE_Items'][0]['publishedDate'].split('T')[0], "%Y-%m-%d").timetuple()))
current_working_directory = os.getcwd()
statments_yaml = open("statements/"+vulnerability_id+"/statement.yaml",'r')
parsed_statments =  yaml.load(statments_yaml, Loader=yaml.FullLoader)
project_url = ''

if  'fixes' in parsed_statments:
    project_url = parsed_statments['fixes'][0]['commits'][0]['repository']
else:
    raise SystemExit("please provide project name")
candidate_commits = list()
project_name=project_url.split('/')[-1]

os.chdir('diff_commits/'+vulnerability_id+"/"+project_name)


utils.gather_candidate_commits(published_timestamp, project_url)

