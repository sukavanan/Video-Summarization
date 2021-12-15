'''
 # @ Author: Sukavanan Nanjundan
 # @ Description: Includes miscellaneous functions
 '''

from functools import reduce
import numpy as np
import pickle as pkl
from config import *
from sklearn.decomposition import PCA

#finds the maximum number of words in a sentence in a list of sentences
def find_max_len(text):
    max_len = 0
    for x in text:
        if len(x.split()) > max_len:
            max_len = len(x.split())
    return max_len

#performs PCA to reduce dimension of BERT embeddings for computational reasons
#performs both vertical and horizontal padding wherever required
#transformed_bert - shape - (n, pad_len, reduced_dim)
def bert_pca(bert, pad_len):
    print("Performing PCA...")
    transformed_bert = np.zeros((bert.shape[0], bert.shape[1], reduced_dim), dtype = np.float32)
    for i in range(len(bert)):
        print(i, end = "\r")
        t_bert = bert[i]
        t_bert = t_bert[~np.all(t_bert == 0, axis = 1)]
        components = min(t_bert.shape)
        if components >= reduced_dim:
            components = reduced_dim
        pca = PCA(n_components = components)
        pca_bert = pca.fit_transform(t_bert)
        if components != reduced_dim:
            vert_pad = np.zeros((components, reduced_dim - components), dtype = np.float32)
            pca_bert = np.concatenate((pca_bert, vert_pad), axis = 1)
        diff = pad_len - len(pca_bert)
        if diff != 0:
            bert_pad = [np.zeros(reduced_dim) for i in range(diff)]
            bert_pad = np.array(bert_pad)
            transformed_bert[i] = np.concatenate((pca_bert, bert_pad), axis = 0)
        else:
            transformed_bert[i] = pca_bert
        del t_bert
    return transformed_bert

def save_as_pickle(data, data_path):
    print("Saving ", data_path, "...")
    with open(data_path, "wb") as fp:
        pkl.dump(data, fp)

def read_pkl_file(data_path):
    with open(data_path, "rb") as fp:
        temp  = pkl.load(fp)
    return fp

#function to get the actual lengths of padded sequences in a batch
def get_lengths(batch, pad_token, lst = False):
    lens = []
    if not lst:
        batch_list = batch.tolist()
        for x in batch_list:
            try:
                lens.append(x.index(pad_token))
            except:
                lens.append(len(x))
    else:
        for x in batch:
            try:
                lens.append(x.split().index(pad_token))
            except:
                lens.append(len(x.split()))
    lens = torch.LongTensor(lens)
    return lens

def accuracy(pred, targ):
    pred = pred.argmax(dim = 1, keepdim = True)
    non_pad_elements = (targ != -1).nonzero()
    correct = pred[non_pad_elements].squeeze(1).eq(targ[non_pad_elements])
    return correct.sum() / torch.FloatTensor([targ[non_pad_elements].shape[0]]).to(device)\

#function to divide the document into chunks of size config.model_word_limit
def divide_chunks(document, n):
    chunks = []
    temp_doc = []
    size_now = 0
    for i in range(len(document)):
        sent = document[i]
        if size_now + len(sent.split()) > n:
            chunks.append(temp_doc)
            temp_doc = [sent]
            size_now = len(sent.split())
        else:
            temp_doc.append(sent)
            size_now += len(sent.split())
    return chunks