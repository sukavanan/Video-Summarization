# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
# %%
import json
import os
# %%
import string

# %%
import nltk
import scipy
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
# %%
from sklearn.feature_extraction.text import TfidfVectorizer


# If there's at most `flexibility` elements between indices, select all of them.
flexibility = 3
target_length = 180 # (only a guideline) Crop might be longer including the important pieces between subs.


try:
	os.chdir(os.path.join(os.getcwd(), 'Jupyter Notebooks'))
	print(os.getcwd())
except:
	pass

with open('../intermediate/output.json') as f:
    data = json.load(fp=f)


stop_words = stopwords.words('english')
lemmatizer = WordNetLemmatizer()

# %% [markdown]
# ### Removing punctuation

for entry in data:
    entry['text'] = entry['text'].translate(str.maketrans('', '', string.punctuation))


# %%
def stop_word_removal(data):
    for caption_entry in data:
        split_dialog = caption_entry['text'].split()
        temp = []
        temp2 = []
        for word in split_dialog:
            if word not in stop_words:
                temp2.append(word)
                temp.append(lemmatizer.lemmatize(word))
        caption_entry['lemmatized'] = ' '.join(temp)
        caption_entry['stop_removed'] = ' '.join(temp2)
    return data


# %%
stopped_stemmed_data = stop_word_removal(data)


# %%
stopped_stemmed_data
print(len(stopped_stemmed_data), stopped_stemmed_data[-1])

# %% [markdown]
# ### Load the document as a corpus and obtain tf-idf vectors


def return_corpus(data):
    corpus = []
    for entry in data:
        # corpus.append(entry['stop_removed'])
        corpus.append(entry['lemmatized'])
    return corpus

corpus = return_corpus(stopped_stemmed_data)

vectorizer = TfidfVectorizer()
tfidf = vectorizer.fit_transform(corpus)

summed_tfidf = scipy.sparse.csr_matrix.sum(tfidf, axis=1)
for entry,element in zip(stopped_stemmed_data, summed_tfidf):
    entry['tfidf_sum'] = element[0,0]


# %%
stopped_stemmed_data[15]


# %%
sorted_list = sorted(stopped_stemmed_data, key=lambda k: k['tfidf_sum'], reverse=True) 


# %%
# Target length of the output video in seconds
naive_summary_elements = []

for entry in sorted_list:
    target_length-=entry['duration']
    naive_summary_elements.append(entry)
    if target_length<0:
        break


# %%
selected_indices = []
for i in sorted(naive_summary_elements, key=lambda k: k['index']):
    selected_indices.append(i['index'])

# %%

flexible_summary = list(selected_indices)
idx_sorted_list = sorted(stopped_stemmed_data, key= lambda k: k['index'])
for idx in range(len(selected_indices)-1):
    # Check succeding flexibility
    if selected_indices[idx+1]-selected_indices[idx] <= flexibility and selected_indices[idx+1]-selected_indices[idx] > 1:
        flexible_summary.extend(list(range(selected_indices[idx]+1,selected_indices[idx+1])))
flexible_summary = sorted(flexible_summary)


# %%
def get_clips_durations(chosen_indices):
    # Find out contiguous sequences of indices and get the timestamps of the videos to cut them.
    sets_of_clips = []
    temp = []
    for idx in range(len(chosen_indices)-1):
        if chosen_indices[idx] not in temp:
            temp.append(chosen_indices[idx])
        if chosen_indices[idx+1]-chosen_indices[idx] == 1:
            temp.append(chosen_indices[idx+1])
            continue
        else:
            sets_of_clips.append(temp)
            temp = []
    return sets_of_clips
sets_of_clips = get_clips_durations(flexible_summary)

final_summary_list = []
for index,clips in enumerate(sets_of_clips):
    data = dict()
    data['clip_no'] = index+1
    data['clip_start'] = stopped_stemmed_data[clips[0]]['start_time']
    data['clip_end'] = stopped_stemmed_data[clips[-1]]['end_time']
    final_summary_list.append(data)

with open('../intermediate/clip_data.json', 'w') as f:
    json.dump(final_summary_list, f)
