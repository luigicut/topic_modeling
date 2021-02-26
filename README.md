# topic_modeling

pip install -r requirements.txt

pip install <your_package> && pip freeze > requirements.txt

dopo tutto il setup e le installazioni delle librerie presenti in requirements.txt per far funzionare spacy bisogna scaricare 

python -m spacy download en

python -m spacy download en_core_web_lg

# install fasttext
https://fasttext.cc/docs/en/python-module.html

# fasttext model into spacy

to create a spacy word vector model starting from fasttext, be in the interested folder and put in terminal

python -m spacy init-model en < new_spacy_model_name > --vectors-loc < fasttext_model >

if problems with yaml not importend use:
python -m pip install PyYAML