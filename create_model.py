# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

# %%
import os
import yaml

# %%

cve = 'CVE-2020-10714'


# %%

current_working_directory = os.getcwd()

statments_yaml = open("statements/"+cve+"/statement.yaml",'r')
parsed_statments =  yaml.load(statments_yaml, Loader=yaml.FullLoader)
project_url = ''
commit_sha = ''

if  'fixes' in parsed_statments:
    project_url = parsed_statments['fixes'][0]['commits'][0]['repository']
    commit_sha = parsed_statments['fixes'][0]['commits'][0]['id']
else:
    raise SystemExit("please provide project URL and fix commit SHA and restart")

project_name=project_url.split('/')[-1]
print(project_name)

os.chdir('diff_commits/'+cve)

output_file = open("project_corpus.txt","a+",encoding="utf8")

for root, dirs, files in os.walk(project_name):
     for file in files:
        with open(os.path.join(root, file), "r") as tmp_file:
            tmp_file.encode('utf-8').strip()
            output_file.write(tmp_file.read()+' ')
            tmp_file.close()

os.chdir(current_working_directory)

# %%
