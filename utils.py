
import spacy
import re
nlp= spacy.load("en_core_web_sm")

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

def dot_case_split(token):
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
    result = re.compile("\\W").split(token)
    if len(result) == 1:
        return 
    return result

def filter_doc(doc):
    if type(doc) != spacy.tokens.doc.Doc:
        raise TypeError("The document should be a spacy.tokens.doc.Doc, which is created by means of nlp(")
    # create a list of tokens where each token must pass the following checks, No punct (spacy prop), No stops (spacy prop), the token must have at least one char, the token length must major then 1  
    for token in doc:
        print(token)
    tokens = [token for token in doc if token.is_punct == False and token.is_stop == False and any(char for char in token.text if char.isalpha()) and len(token) > 1] #token.pos_ in ['VERB', 'NOUN', 'PROPN', 'ADJ'] and 
    result = list()
    for token in tokens:
        tmp_result = list()
        if camel_case_split(token.text):
            tmp_result = [camel_case_token.lemma_ for camel_case_token in nlp(' '.join(camel_case_split(token.text)))]
            for token in tmp_result:
                if snake_case_split(token):
                    tmp_result = [snake_case_token.lemma_ for snake_case_token in nlp(' '.join(snake_case_split(token)))]
                    for token in tmp_result:
                        if dot_case_split(token):
                            tmp_result = [dot_case_token.lemma_ for dot_case_token in nlp(' '.join(dot_case_split(token)))]
                            result += [res for res in tmp_result if not res.isspace()]
                elif dot_case_split(token):
                    tmp_result = [dot_case_token.lemma_ for dot_case_token in nlp(' '.join(dot_case_split(token)))]
                    result += [res for res in tmp_result if not res.isspace()]
                else:
                  #check if token not contains only spaces 
                  if not token.isspace():
                    result.append(str(token).lower())
            # result += [res for res in tmp_result if not res.isspace()]
        elif snake_case_split(token.text):
            tmp_result = [snake_case_token.lemma_ for snake_case_token in nlp(' '.join(snake_case_split(token.text)))]
            for token in tmp_result:
                if dot_case_split(token):
                    tmp_result = [dot_case_token.lemma_ for dot_case_token in nlp(' '.join(dot_case_split(token)))]
                    result += [res for res in tmp_result if not res.isspace()]
        elif dot_case_split(token.text):
            result += [dot_case_token.lemma_ for dot_case_token in nlp(' '.join(dot_case_split(token.text))) if not dot_case_token.lemma_.isspace()]

        else:
            result.append(str(token.lemma_).lower())

    return ' '.join(result)


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