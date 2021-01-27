
import spacy
import re
nlp= spacy.load("en_core_web_lg")

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
            tmp_result = [special_char_token for special_char_token in nlp(' '.join(special_chars_split(token.text))) if string_not_spaces_or_one_char(special_char_token.text)]
            for sc_token in tmp_result:
                if camel_case_split(sc_token.text):
                    result += [camel_case_token.lemma_ for camel_case_token in nlp(' '.join(camel_case_split(sc_token.text)))]
                else:
                    result.append(str(sc_token.lemma_).lower()) 
        elif camel_case_split(token.text): 
            result += [camel_case_token.lemma_ for camel_case_token in nlp(' '.join(camel_case_split(token.text)))]
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