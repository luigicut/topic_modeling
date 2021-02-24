#%% 
import os


def main(cve, predictionType):
    current_working_directory = os.getcwd()
    os.chdir(current_working_directory+"/diff_commits/"+cve)
    file_to_order = ''
    if predictionType == 'spacy':
      file_to_order = open("commits_similarity_file.txt","r")
    else:
      file_to_order = open("commits_similarity_file_fasttext.txt","r")
    # file_to_order = open("file_project_list_stars.txt","r")
    list_to_order = list()
    for lines in file_to_order.readlines():
        sha, value = lines.split(",")
        value = value.split("\n")[0]
        list_to_order.append((sha,value))
    file_to_order.close()
    file_to_replace = ''
    if predictionType == 'spacy':
      file_to_replace = open("order_commits_similarity_file.txt","w")
    else:
      file_to_replace = open("order_commits_similarity_file_fasttext.txt","w")
    # file_to_replace = open("commits_similarity_file.txt","w")
    # file_to_replace = open("commits_similarity_file_fasttext.txt","w")
    # file_to_replace = open("file_project_list_stars.txt","w")
    list_to_order.sort(reverse=True, key=lambda x:x[1])
    # list_to_order.sort(reverse=True, key=lambda x:int(x[1]))
    for el in list_to_order:
      file_to_replace.writelines(str(el)+"\n")
    file_to_replace.close()
    print(str(list_to_order))
    os.chdir(current_working_directory)
# %%
# if __name__ == "__main__":
#   main()