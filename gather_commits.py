#%% 
import os, requests, json
import yaml
import time
from datetime import datetime

# vulnerability_id ="CVE-2020-1961"
current_working_directory = os.getcwd()
# os.environ['GIT_CACHE'] = current_working_directory + '/diff_commits/'+vulnerability_id
import utils

#%%
def get_commit_list(vulnerability_id, project_url):
    nist_nvd_request_url = "https://services.nvd.nist.gov/rest/json/cve/1.0/"

    r = requests.get(nist_nvd_request_url+vulnerability_id)
    assert r.ok == True, "vulnerability ID {} is not in the NVD".format(vulnerability_id)
    cve_content = r.json()
    timestamp_from_json = cve_content['result']['CVE_Items'][0]['publishedDate'].split('T')[0]
    date = datetime.strptime(timestamp_from_json, '%Y-%m-%d')
    timestamp = str((date - datetime(1970, 1, 1)).total_seconds()*1000)
    published_timestamp = time.mktime(datetime.fromtimestamp(int(timestamp[:-2])/1000.0).timetuple())
    # statments_yaml = open("statements/"+vulnerability_id+"/statement.yaml",'r')
    # parsed_statments =  yaml.load(statments_yaml, Loader=yaml.FullLoader)
    # project_url = ''

    # if  'fixes' in parsed_statments:
    #     project_url = parsed_statments['fixes'][0]['commits'][0]['repository']
    # else:
    #     raise SystemExit("please provide project name")
    
    os.environ['GIT_CACHE'] = current_working_directory + '/diff_commits/'+vulnerability_id
    commit_list = utils.gather_candidate_commits(published_timestamp, project_url)

    return commit_list




# %%
