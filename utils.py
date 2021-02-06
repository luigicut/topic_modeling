import spacy, datetime, os
import re
import requests
from core import Git, Commit
import random
import chardet
from shutil import rmtree

nlp= spacy.load("en_core_web_lg")
GIT_CACHE = ''
if 'GIT_CACHE' in os.environ:
    GIT_CACHE = os.environ['GIT_CACHE']

def camel_case_split(token):
    '''
    Splits a CamelCase token into a list of tokens,

    Input:
        token (str): the token that should be split if it is in CamelCase

    Returns:
        None: if the token is not in CamelCase
        list: 'CamelCase' --> ['CamelCase', 'camel', 'case']
    '''
    if type(token) != str:
        raise TypeError('The provided token should be a str data type but is of type {}.'.format(type(token)))

    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', token)
    result = [m.group(0).lower() for m in matches]
    if len(result) == 1:
        return
    return result

def snake_case_split(token):
    '''
    Splits a snake_case token into a list of tokens,

    Input:
        token (str): the token that should be split if it is in CamelCase

    Returns:
        None: if the token is not in CamelCase
        list: 'CamelCase' --> ['CamelCase', 'camel', 'case']
    '''
    if type(token) != str:
        raise TypeError('The provided token should be a str data type but is of type {}.'.format(type(token)))

    result = token.split('_')
    if len(result) == 1:
        return 
    return result

def special_chars_split(token):
    '''
    Splits a dot.case token into a list of tokens,

    Input:
        token (str): the token that should be split if it is in dot.case

    Returns:
        None: if the token is not in dot.case
        list: 'dot.case' --> ['dot.case', 'dot', 'case']
    '''
    if type(token) != str:
        raise TypeError('The provided token should be a str data type but is of type {}.'.format(type(token)))

    # result = token.split(".")
    # String lines[] = string.split("\r?\n")
    tmp_result = re.compile("\\W").split(token)
    result = list()
    for res in tmp_result:
        if len(res.split('_')) > 1:
            result += res.split('_')
        else:
            result.append(str(res))
    if len(result) == 1:
        return 
    return result


def string_not_spaces_or_one_char(s):
    return not s.isspace() and len(s) > 1

def str_not_special_upper(s):
    '''
    Checks if a string contains special characters and if contains at least one uppercase letter
    '''
    return bool(re.match('^[a-zA-Z0-9]*$',s)) and not any(x.isupper() for x in s)


def split_funct(token, result):
    if str_not_special_upper(token.lemma_):
      if string_not_spaces_or_one_char(token.lemma_):
        result.append(str(token.lemma_).lower())
      return
    else:
        if camel_case_split(token.text):
            temp_result = [camel_case_token.lemma_ for camel_case_token in nlp(' '.join(camel_case_split(token.text)))]
            for new_token in nlp(' '.join(temp_result)):
                split_funct(new_token, result)
        if snake_case_split(token.text):
            temp_result = [snake_case_token.lemma_ for snake_case_token in nlp(' '.join(snake_case_split(token.text)))]
            for new_token in nlp(' '.join(temp_result)):
                split_funct(new_token, result)
        if special_chars_split(token.text):
            temp_result = [dot_case_token.lemma_ for dot_case_token in nlp(' '.join(special_chars_split(token.text)))]
            for new_token in nlp(' '.join(temp_result)):
                split_funct(new_token, result)

def filter_doc(doc):
    if type(doc) != spacy.tokens.doc.Doc:
        raise TypeError("The document should be a spacy.tokens.doc.Doc, which is created by means of nlp(")
    # create a list of tokens where each token must pass the following checks, No punct (spacy prop), No stops (spacy prop), the token must have at least one char, the token length must major then 1  
    # for token in doc:
    #     print(token)
    tokens = [token for token in doc if token.is_punct == False and token.is_stop == False and any(char for char in token.text if char.isalpha()) and len(token) > 1] #token.pos_ in ['VERB', 'NOUN', 'PROPN', 'ADJ'] and 
    result = list()
    
    for token in tokens:
        tmp_result = list()
        if special_chars_split(token.text):
            tmp_result = [special_char_token for special_char_token in nlp(' '.join(special_chars_split(token.text))) if string_not_spaces_or_one_char(special_char_token.lemma_)]
            for sc_token in tmp_result:
                if camel_case_split(sc_token.text):
                    result += [camel_case_token.lemma_ for camel_case_token in nlp(' '.join(camel_case_split(sc_token.text))) if string_not_spaces_or_one_char(camel_case_token.lemma_)]
                else:
                    result.append(str(sc_token.lemma_).lower()) 
        elif camel_case_split(token.text): 
            result += [camel_case_token.lemma_ for camel_case_token in nlp(' '.join(camel_case_split(token.text)))  if string_not_spaces_or_one_char(camel_case_token.lemma_)]
        else:
            result.append(str(token.lemma_).lower()) 

    return ' '.join(result)

# def filter_doc(doc):
#     if type(doc) != spacy.tokens.doc.Doc:
#         raise TypeError("The document should be a spacy.tokens.doc.Doc, which is created by means of nlp(")
#     # create a list of tokens where each token must pass the following checks, No punct (spacy prop), No stops (spacy prop), the token must have at least one char, the token length must major then 1  
#     # for token in doc:
#     #     print(token)
#     tokens = [token for token in doc if token.is_punct == False and token.is_stop == False and any(char for char in token.text if char.isalpha()) and len(token) > 1] #token.pos_ in ['VERB', 'NOUN', 'PROPN', 'ADJ'] and 
#     result = list()
#     for token in tokens:
#         tmp_result = list()
#         # split_funct(token, result)
#         if camel_case_split(token.text):
#             tmp_result = [camel_case_token.lemma_ for camel_case_token in nlp(' '.join(camel_case_split(token.text)))]
#             for token in tmp_result:
#                 if snake_case_split(token):
#                     tmp_result = [snake_case_token.lemma_ for snake_case_token in nlp(' '.join(snake_case_split(token)))]
#                     for token in tmp_result:
#                         if special_chars_split(token):
#                             tmp_result = [dot_case_token.lemma_ for dot_case_token in nlp(' '.join(special_chars_split(token)))]
#                             result += [res for res in tmp_result if string_not_spaces_or_one_char(res)]
#                 elif special_chars_split(token):
#                     tmp_result = [dot_case_token.lemma_ for dot_case_token in nlp(' '.join(special_chars_split(token)))]
#                     result += [res for res in tmp_result if string_not_spaces_or_one_char(res)]
#                 else:
#                   #check if token not contains only spaces 
#                   if string_not_spaces_or_one_char(token):
#                     result.append(str(token).lower())
#         elif snake_case_split(token.text):
#             tmp_result = [snake_case_token.lemma_ for snake_case_token in nlp(' '.join(snake_case_split(token.text)))]
#             for token in tmp_result:
#                 if special_chars_split(token):
#                     tmp_result = [dot_case_token.lemma_ for dot_case_token in nlp(' '.join(special_chars_split(token)))]
#                     result += [res for res in tmp_result if string_not_spaces_or_one_char(res)]
#         elif special_chars_split(token.text):
#             result += [dot_case_token.lemma_ for dot_case_token in nlp(' '.join(special_chars_split(token.text))) if string_not_spaces_or_one_char(dot_case_token.lemma_)]

#         else:
#             result.append(str(token.lemma_).lower())

#     return ' '.join(result)


def text_into_chunks(text, chunk_size=1000):
    '''
    Yield successive n-sized chunks from list.
    '''
    if type(text) == list:
        text = ' '.join(text)
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


def simpler_filter_text(text):
    ''' Similar to filter_text but without options:
            will be lemmatized and returned as a string
    '''

    # when a list is provided concatenate it into a string
    if type(text) == list:
        text = ' '.join([str(line) for line in text])

    # filter text, needs to be in chunks due to spacy maximum of 1000000 characters
    result = ' '.join([filter_doc(nlp(chunk)) for chunk in text_into_chunks(text, chunk_size = 10000)]).lower()
    return  result


def timestamp_to_timestamp_interval(timestamp, days_before, days_after):
    since = str(int((datetime.datetime.fromtimestamp(int(timestamp)) - datetime.timedelta(days=int(days_before))).timestamp()))
    until = str(int((datetime.datetime.fromtimestamp(int(timestamp)) + datetime.timedelta(days=int(days_after))).timestamp()))
    return since, until

def get_commit_ids_between_timestamp(since, until, git_repo, repository_url):
    '''
    Based on git_explorer.core.get_commits()
        The order is from newest to oldest: the result[0] is the most recent one (larger timestamp), the result[-1] is the oldest (smallest timestamp)
    
    Input:
        since (str/int): timestamp in format i.e. '1230185619'
        until (str/int): timestamp in format i.e. '1271076761'
    '''
    # if git_repo == None and repository_url ==None:
    #     raise ValueError('Provide a git_repo or a repository_url')
  
    if int(float(since)) >= int(float(until)):
        raise ValueError('The timestamps provided result in an interval without commit IDs, as since >= until.')
    
    since = int(float(since))
    until = int(float(until))
    if git_repo == None:
        git_repo = Git(repository_url, cache_path=GIT_CACHE)
        git_repo.clone(skip_existing=True)
        
    # create git command
    cmd = ["git", "rev-list", "--all", "--remotes"]
    cmd.append("--since=" + str(since))
    cmd.append("--until=" + str(until))
    
    try:
        out = git_repo._exec.run(cmd)
    except:
        print("Git command failed. Could not obtain commit ids.")
        return
    
    return [l.strip() for l in out]

def gather_candidate_commits(published_timestamp, project_url):
        since, until = timestamp_to_timestamp_interval(published_timestamp, days_before=183, days_after=100)

        ### Add commits before NVD release with maximum to add
        commit_ids_to_add_before = get_commit_ids_between_timestamp(str(since), str(published_timestamp), git_repo=None, repository_url=project_url)
        if len(commit_ids_to_add_before) > 5215:
            commit_ids_to_add_before = commit_ids_to_add_before[:5215] #add the 5215 closest before the NVD release date

        ### Add commits after NVD release with a maximum to add
        commit_ids_to_add_after = get_commit_ids_between_timestamp(str(published_timestamp), str(until), git_repo=None, repository_url=project_url)
        if len(commit_ids_to_add_after) > 100:
            commit_ids_to_add_after = commit_ids_to_add_after[-100:] #add the 100 closest before the NVD release date

        # gather candidate commits
        # print(commit_ids_to_add_before + commit_ids_to_add_after)
        #if len(candidate_commits) > 0:
        # if  candidate_commits != None and len(candidate_commits) > 0:
        #     # validate_database_coverage()
        #     print("CANDIDATE commits in gather candidate commit rank.py")
        #     print("self candidate commit :", candidate_commits)
        #     # candidate_commits = filter.filter_commits_on_files_changed_extensions(candidate_commits, connection, verbose=self.verbose)
        # else:
        #     print("No candidates found.")

        return commit_ids_to_add_before + commit_ids_to_add_after

def reservoir_sampling(input_list, N):
    sample = []
    for i, line in enumerate(input_list):
        if i < N:
            sample.append(line)
        elif i >= N and random.random() < N / float(i + 1):
            replace = random.randint(0, len(sample) - 1)
            sample[replace] = line
    return sample


def extract_files_from_diff(project_url,commit_sha, vulnerability_id):
    # url = project_url+"/commit/"+commit_sha+".diff"
    # r = requests.get(url, allow_redirects=True)
    git_repo = Git(project_url, cache_path=GIT_CACHE)
    git_repo.clone(skip_existing=True)

    commit = Commit(git_repo, commit_sha)

    diff = commit._exec.run(['git', 'diff', commit._id + "^.." + commit._id])

    to_create_file = open(commit_sha+'.diff', 'wb',)
    for item in diff:
        to_create_file.write(("%s\n" % item).encode('utf8'))
    # f.close()
    # to_create_file.write(diff)
    to_create_file.close()
    # diff_file = open(commit_sha+'.diff', "r", encoding="utf8")

    byte_tmp_file = open(commit_sha+'.diff', "rb")
    file_type = chardet.detect(byte_tmp_file.read())['encoding']
    paths_list = list()
    if str(file_type) == 'utf-8' or str(file_type) == 'ascii' or str(file_type) == 'TIS-620':
        with open(commit_sha+'.diff', "r", encoding="utf8") as diff_file:
            lines = diff_file.readlines()
            for i in range(0, len(lines)):
                if (lines[i].startswith('diff --git ')):
                    if not lines[i+1].startswith('deleted'):
                        path = lines[i].split(' b/')[1].rstrip("\n")
                        paths_list.append(path)
            
        # for line in diff_file.readlines():
        #     if (line.startswith('diff --git ')): 

        #         path = line.split(' b/')[1].rstrip("\n")
        #         paths_list.append(path)
        # os.environ['GIT_CACHE'] = current_working_directory + '/diff_commits/'+vulnerability_id
        # git_repo = Git(project_url, cache_path=GIT_CACHE)
        # git_repo.clone(skip_existing=True)

    for path in paths_list: 
        file_name = path.split('/')[-1].rstrip("\n")
        file_type = file_name.split('.')[-1]
        if file_type == 'java':
            cmd = ["git", "show", commit_sha+":"+path]
            try:
                out = git_repo._exec.run(cmd)
                with open("committed_files/"+file_name,"w") as f:
                    for item in out:
                        f.write("%s\n" % item)
                    f.close()
            except:
                print("Git command failed. Could not obtain commit ids.")
                return

def folder_cleaner(commit, candidate_commits_path):
    os.chdir("..")
    if len(os.listdir(candidate_commits_path+"/"+commit+"/committed_files")) == 0 :
        rmtree(commit, ignore_errors=True)



# def license_remove(file):


def license_remove(txt, delim=('/*', '*/')):
    'Strips first nest of block comments'
 
    deliml, delimr = delim
    out = ''
    if deliml in txt:
        indx = txt.index(deliml)
        out += txt[:indx]
        txt = txt[indx+len(deliml):]
        # txt = _commentstripper(txt, delim)
        assert delimr in txt, 'Cannot find closing comment delimiter in ' + txt
        indx = txt.index(delimr)
        out += txt[(indx+len(delimr)):]
    else:
        out = txt
    return out
 

# def commentstripper(txt, delim=('/*', '*/')):
#     'Strips nests of block comments'
 
#     deliml, delimr = delim
#     while deliml in txt:
#         txt = _commentstripper(txt, delim)
#     return txt