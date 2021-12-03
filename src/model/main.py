import pandas as pd
import numpy as np
import torch
from model.config import *
from model.misc import *
from model.data_loader import *
from model.bert_embeddings import *

df = create_data()
df = preprocess_data(df)
df, labels = create_labels(df, True)
tokenized_text, torch_idx_text, torch_seg_ids = create_tensors_BERT(df.text)
bert_embeddings = get_embeddings(torch_idx_text, torch_seg_ids)
text, bert = embeddings_to_words(tokenized_text, bert_embeddings)
lstm_pad_len = find_max_len(text)
text = df.text.values
text, labels, bert = prepare_data_for_LSTM(text, labels, bert, lstm_pad_len)
save_as_pickle(text, text_pkl)
save_as_pickle(labels, labels_pkl)
save_as_pickle(bert, bert_pkl)
transformed_bert = bert_pca(bert, lstm_pad_len)
save_as_pickle(transformed_bert, bert_reduced_pkl)
