#%% 
import os
vulnerability_id = 'CVE-2019-17572'
current_working_directory = os.getcwd()
# os.environ['GIT_CACHE'] = current_working_directory + '/diff_commits/'+vulnerability_id
os.environ['GIT_CACHE'] = current_working_directory + "/GIT_CACHE"
GIT_CACHE = os.environ['GIT_CACHE']
from scipy import spatial
import fasttext
import gather_commits
import re
import yaml


#%%
current_working_directory = os.getcwd()
statments_yaml = open("statements/"+vulnerability_id+"/statement.yaml",'r')
parsed_statments =  yaml.load(statments_yaml, Loader=yaml.FullLoader)
project_url = ''
commit_sha = ''

if  'fixes' in parsed_statments:
    project_url = parsed_statments['fixes'][0]['commits'][0]['repository']
    commit_sha = parsed_statments['fixes'][0]['commits'][0]['id']
else:
    raise SystemExit("please provide project URL and fix commit SHA and restart")
print(project_url)

project_name=project_url.split('/')[-1]
print(project_name)

cve_path = current_working_directory+'/diff_commits/'+vulnerability_id
os.chdir(cve_path)
model = fasttext.load_model(current_working_directory+"/GIT_CACHE/"+project_name+"_models"+"/fasttext_model/model_"+project_name+".bin")
cve_keywords = list()
os.chdir(cve_path)
with open("cve_description_keywords.txt","r") as cve_keywords_file:
    cve_keywords = cve_keywords_file.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
cve_keywords = [x.strip() for x in cve_keywords] 
print(str(cve_keywords))
# os.chdir(candidate_commits_path)
os.chdir(current_working_directory)
commit_list = gather_commits.get_commit_list(vulnerability_id, project_url)
os.chdir(cve_path)
project_commits_path = GIT_CACHE+"/"+project_name+"_commits"
for commit in commit_list:
    os.chdir(project_commits_path)
    if os.path.exists(commit):
        prediction_joint_file = open(commit+"/prediction_joint_corpus_"+commit+".txt","r")
        prediction_words_all_list = re.findall(r"'(.*?)'", prediction_joint_file.read())
        # prediction_words_list = prediction_words_all_list[:int(len(prediction_words_all_list)/2)]
        prediction_words_list = prediction_words_all_list[:49]
        # print(str(prediction_words_list))
        # if commit == "e07263dedad7ed44e188abb11260fa3061afadc4":
        similarity_avg = 0
        for key in cve_keywords:
            max_value = -1
            for pred in prediction_words_list:
                # if pred == 'expression' and key == 'expression':
                k = model.get_word_vector(key)
                p = model.get_word_vector(pred)
                # print(k)
                # print(p)
                # print(str(spatial.distance.cosine(k,p)))
                cosine_distance = spatial.distance.cosine(k,p)
                similarity = 1-cosine_distance
                if similarity > max_value:
                    max_value = similarity
            # print(key+" : "+str(max_value))
            similarity_avg += max_value
        similarity_avg = similarity_avg/len(cve_keywords) 
        os.chdir(cve_path)   
        commits_similarity_file = open("commits_similarity_file_fasttext.txt","a+")
        commits_similarity_file.writelines(commit+","+str(similarity_avg)+"\n")
commits_similarity_file.close()
# %%
