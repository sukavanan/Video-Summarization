import json
import os
import string
import time as t

import nltk
import scipy
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer

from common_functions import FLEXIBILITY, TARGET_LENGTH

def strip_punctuation(data):
    for entry in data:
        entry['text'] = entry['text'].translate(str.maketrans('', '', string.punctuation))
    return data

def stop_word_removal(data):
    stop_words = stopwords.words('english')
    lemmatizer = WordNetLemmatizer()
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

def return_corpus(data):
    # Return just the lemmatized/stop_removed strings from the main dataset
    corpus = []
    for entry in data:
        # corpus.append(entry['stop_removed'])
        corpus.append(entry['lemmatized'])
    return corpus

def return_naive_summary(sorted_list, length):
    naive_summary_elements = []
    for entry in sorted_list:
        length-=entry['duration']
        naive_summary_elements.append(entry)
        if length<0:
            break
    return naive_summary_elements

def indices_selected(naive_summary_elements):
    selected_indices = []
    for i in sorted(naive_summary_elements, key=lambda k: k['index']):
        selected_indices.append(i['index'])
    return selected_indices

def flexibly_extend_summary(selected_indices):
    flexible_summary = list(selected_indices)
    for idx in range(len(selected_indices)-1):
        # Check succeeding FLEXIBILITY
        if selected_indices[idx+1]-selected_indices[idx] <= FLEXIBILITY and selected_indices[idx+1]-selected_indices[idx] > 1:
            flexible_summary.extend(list(range(selected_indices[idx]+1,selected_indices[idx+1])))
    flexible_summary = sorted(flexible_summary)
    return flexible_summary

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

def get_final_clip_timestamps(sets_of_clips, stopped_stemmed_data):
    final_summary_list = []
    for index,clips in enumerate(sets_of_clips):
        data = dict()
        data['clip_no'] = index+1
        # print(clips[0], stopped_stemmed_data[clips[0]]['start_time'])
        data['clip_start'] = stopped_stemmed_data[clips[0]]['start_time']
        data['clip_end'] = stopped_stemmed_data[clips[-1]]['end_time']
        final_summary_list.append(data)
    return final_summary_list

def return_clips(path, output_path='../intermediate/clip_data.json'):
    with open(path) as f:
        data = json.load(fp=f)

    data = strip_punctuation(data)
    stopped_stemmed_data = stop_word_removal(data)

    corpus = return_corpus(stopped_stemmed_data)

    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform(corpus)

    summed_tfidf = scipy.sparse.csr_matrix.sum(tfidf, axis=1)
    for entry,element in zip(stopped_stemmed_data, summed_tfidf):
        entry['tfidf_sum'] = element[0,0]

    sorted_list = sorted(stopped_stemmed_data, key=lambda k: k['tfidf_sum'], reverse=True) 

    naive_summary_elements = return_naive_summary(sorted_list, TARGET_LENGTH)
    selected_indices = indices_selected(naive_summary_elements)

    flexible_summary = flexibly_extend_summary(selected_indices)

    sets_of_clips = get_clips_durations(flexible_summary)
    final_summary_list = get_final_clip_timestamps(sets_of_clips, stopped_stemmed_data)
    with open(output_path, 'w') as f:
        json.dump(final_summary_list, f)

if __name__ == "__main__":
   
    start_time = t.time()
    return_clips('../intermediate/Hypothesis testing-II.json')
    print(f"Completed text parsing {round(t.time()-start_time, 2)} seconds")