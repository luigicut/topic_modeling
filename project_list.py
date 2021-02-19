#%%
import yaml
import os

#%%
project_list= list()
output_file = open("file_project_list.txt", "a+")
for root, dirs, files in os.walk("statements"):
    for file in files:
        with open(os.path.join(root, file), "r", encoding= "utf-8") as statments_yaml:
        # statments_yaml = open("statements/"+vulnerability_id+"/statement.yaml",'r')
            file_type = statments_yaml.name.split('.')[-1]
            # print(statments_yaml.name)
            if file_type == 'yaml':
                # print(statments_yaml.name)
                parsed_statments =  yaml.load(statments_yaml, Loader=yaml.FullLoader)
                project_url = ''
                if 'fixes' in parsed_statments:
                    project_url = parsed_statments['fixes'][0]['commits'][0]['repository']
                else:
                    print("no url available")

                if project_url not in project_list and "https://github.com/" in project_url:
                    project_list.append(project_url)
                    output_file.writelines(project_url+"\n")

output_file.close()
print(len(project_list))
