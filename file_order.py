#%% 

file_to_order = open("commits_similarity_file_fasttext.txt","r")
list_to_order = list()
for lines in file_to_order.readlines():
    sha, value = lines.split(",")
    value = value.split("\n")[0]
    list_to_order.append((sha,value))

list_to_order.sort(reverse=True, key=lambda x:x[1])

print(str(list_to_order))

# %%
