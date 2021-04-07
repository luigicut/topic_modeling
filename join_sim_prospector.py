# %%
import pandas as pd

# %%
similarity_df = pd.DataFrame()
prospector_df = pd.DataFrame()

similarity_df = pd.read_csv('final_results_all_commits_prospector.csv', index_col=0)
prospector_df = pd.read_csv('prospector_ranking_vector_df_all_components.csv', index_col=0)

similarity_df.head()

# %%
prospector_df.head()


# %%
# def add_one(x):
# 	return x + 1

# prospector_df[1] = prospector_df['commit_id'].apply(add_one)


result = pd.merge(similarity_df, prospector_df, on=['commit_id', 'vulnerability_id'], how='inner')

# %%
result.head()
#ne dobbiamo fare 2
#2 sono csv
#

#dataframe 1
#deve avere la struttura di prospector_df, in pratica dobbiamo filtrare le righe i cui commit non sono presenti 
#in similarity df. questo dataframe ci serve per riallenare il modello senza le nostre feature
#così poi possiamo fare il paragone sui risultati

#dataframe 2
 #deve contenere lo stesso numero di righe dell'uno, con in più i nostri valori features
 

# %%
cols = list(result.columns.values)
print(cols)
# %%
result = result[['commit_id', 'similarity_spacy', 'similarity_fasttext', 'vulnerability_id_in_message', 'other_CVE_in_message', 'n_hunks', 'avg_hunk_size', 'n_changed_files', 'git_issue_reference', 'contains_jira_reference', 'path_similarity_score', 'message_score', 'changed_files_score', 'git_diff_score', 'message_score_reference_content', 'changed_files_score_reference_content', 'git_diff_score_reference_content', 'message_score_code_tokens', 'changed_files_score_code_tokens', 'git_diff_score_code_tokens', 'time_distance_before', 'time_distance_after', 'reachability_score', 'referred_to_by_nvd', 'referred_to_by_advisories', 'vulnerability_timestamp', 'vulnerability_id']]
# %%
result.head()
# %%

result.to_csv('dataframe_all_features.csv') 

# %%
result.drop(columns=['similarity_spacy', 'similarity_fasttext'], inplace=True)
# %%
result.to_csv('dataframe_prospector_features.csv') 
