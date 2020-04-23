# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
# %%
import json
import os
# %%
import string
import time as t
# %%
import nltk
import scipy
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
# %%
from sklearn.feature_extraction.text import TfidfVectorizer

from common_functions import FLEXIBILITY, TARGET_LENGTH

start_time = t.time()


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
sorted_list = sorted(stopped_stemmed_data, key=lambda k: k['tfidf_sum'], reverse=True) 


x = []
for entry in sorted_list:
    e = entry['index'],entry['tfidf_sum'],entry['duration']
    x.append(e)
# print(x)

# %%
# Target length of the output video in seconds
naive_summary_elements = []

for entry in sorted_list:
    TARGET_LENGTH-=entry['duration']
    naive_summary_elements.append(entry)
    if TARGET_LENGTH<0:
        break


# %%
selected_indices = []
for i in sorted(naive_summary_elements, key=lambda k: k['index']):
    selected_indices.append(i['index'])

# %%

flexible_summary = list(selected_indices)
idx_sorted_list = sorted(stopped_stemmed_data, key= lambda k: k['index'])
for idx in range(len(selected_indices)-1):
    # Check succeeding FLEXIBILITY
    if selected_indices[idx+1]-selected_indices[idx] <= FLEXIBILITY and selected_indices[idx+1]-selected_indices[idx] > 1:
        flexible_summary.extend(list(range(selected_indices[idx]+1,selected_indices[idx+1])))
flexible_summary = sorted(flexible_summary)

# Create colors for bar gr
# colors = []
# for i in range(len(stopped_stemmed_data)):
#     if i in flexible_summary and i not in selected_indices:
#         colors.append('g')
#     elif i in selected_indices:
#         colors.append('b')
#     else:
#         colors.append('r')
# # %%
# import matplotlib.pyplot as plt
# y = []
# x = []
# for entry in stopped_stemmed_data:
#     y.append(entry['tfidf_sum'])
#     x.append(entry['index'])
# # print(x,y)
# plt.bar(x,y, color=colors)
# plt.xlabel("Subtitle Index")
# plt.ylabel("Tf-idf Sum")
# plt.legend()
# plt.show()


# Generate an Output Subtitle

# count = 1
# output_string = ""
# for i in flexible_summary:
#     output_string += f"{count}\n{data[i]['start_time']} --> {data[i]['end_time']}\n{data[i]['text']}\n\n"
#     count += 1
# with open("../outputs/output.srt", "w") as f:
#     f.write(output_string)

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

print(sets_of_clips, len(sets_of_clips))

final_summary_list = []
for index,clips in enumerate(sets_of_clips):
    data = dict()
    data['clip_no'] = index+1
    # print(clips[0], stopped_stemmed_data[clips[0]]['start_time'])
    data['clip_start'] = stopped_stemmed_data[clips[0]]['start_time']
    data['clip_end'] = stopped_stemmed_data[clips[-1]]['end_time']
    final_summary_list.append(data)

with open('../intermediate/clip_data.json', 'w') as f:
    json.dump(final_summary_list, f)
    
print(f"Completed text parsing {round(t.time()-start_time, 2)} seconds")
