'''
 # @ Author: Sukavanan Nanjundan
 # @ Description: Includes dataloader class and functions to create, pre-process and label the textual data from the DebateSum dataset
 '''

import pandas as pd
import numpy as np
import warnings
from torch.utils.data.dataset import ConcatDataset
from model.config import *
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset, Dataset
warnings.filterwarnings("ignore")

class Dataset(object):
    def __getitem__(self, index):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __add__(self, other):
        return ConcatDataset([self, other])

class data(Dataset):
    def __init__(self, inputs, transform = None):
        self.data = inputs
        self.transform = transform
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, index):
        inputs = self.data[index][0]
        label = self.data[index][1]
        if self.transform is not None:
            inputs = self.transform(inputs)
            
        return inputs, label

#returns dataframe containing original text and summary
def create_data():
    print("Loading Data...")
    data = pd.read_csv(data_path)
    data = data[data["#WordsDocument"] <= word_limit]
    df = pd.DataFrame(data[["Full-Document", "Extract"]], index = None)
    df = df.reset_index()
    df = df.drop(["index"], axis = 1)
    df = df.rename(columns = {"Full-Document": "text", "Extract": "summary"})
    return df

#returns preprocessed dataframe
def preprocess_data(df):
    print("Preprocessing Data...")
    df.text = df.text.str.lower()
    df.text = df.text.replace("[^a-zA-Z ]", "", regex = True)
    df.text = df.text.apply(lambda x: " ".join([word for word in x.split() if word not in stop]))
    df.text = df.text.replace(df.text.values, cls + " " + df.text.values + " " + sep)

    df.summary = df.summary.str.lower()
    df.summary = df.summary.replace("[^a-zA-Z ]", "", regex = True)
    df.summary = df.summary.apply(lambda x: " ".join([word for word in x.split() if word not in stop]))
    df.summary = df.summary.replace(" +", " ", regex = True)
    return df

#creates 0/1 labels for words in the text field denoting whether they are in the summary
def create_labels(df, save = False):
    print("Creating Labels...")
    df["labels"] = None
    labels = []
    for i in range(len(df)):
        text = df.iloc[[i]].text.values[0].split()
        summary = df.iloc[[i]].summary.values[0].split()
        temp = [0] * len(text)
        prev_idx = -1
        for j in range(len(summary)):
            try:
                temp_idx = text[prev_idx + 1: ].index(summary[j]) + prev_idx + 1
                temp[temp_idx] = 1
                prev_idx = temp_idx
            except:
                continue
        labels.append(temp)
        df.at[i, 'labels'] = temp 
    
    if save:
        df.to_csv(labeled_data_path, index = False)
    return df, labels

#takes in text, labels and bert embeddings as input(type - list) and returns the same with the length padded to the maximum length of the text
#also removes the [CLS] and [SEP] tags from the inputs
#bert - shape - (n, pad_len, bert_emd_dim)
def prepare_data_for_LSTM(text, labels, bert, pad_len):
    bert = [x[1:-1] for x in bert]
    text = [x[6:-6] for x in text]
    print(labels)
    if labels != None:
        labels = [x[1:-1] for x in labels]
    dim = bert_emb_dim
    for i in range(len(text)):
        diff = pad_len - len(text[i].split())
        if diff != 0:
            text[i] = text[i] + (" <pad>" * diff)
            if labels != None:
                labels[i] = labels[i] + ([-1] * diff)
            bert_pad = [np.zeros(dim) for i in range(diff)]
            bert[i] = bert[i] + bert_pad
            bert[i] = np.array(bert[i], dtype = np.float32)
    bert = np.array(bert, dtype = np.float32)
    if labels != None:
        return text, labels, bert
    else:
        return text, bert

def split_data(bert, labels, dev_test_ratio, test_ratio):
    x_train, x_test, y_train, y_test = train_test_split(bert, labels, test_size = dev_test_ratio, random_state = 42)
    x_dev, x_test, y_dev, y_test = train_test_split(x_test, y_test, test_size = test_ratio, random_state = 42)
    return x_train, x_dev, x_test, y_train, y_dev, y_test

def create_data_loaders(x_train, y_train, x_dev, y_dev):
    train_dataset = TensorDataset(x_train, y_train)
    train_dataset = data(train_dataset)
    dev_dataset = TensorDataset(x_dev, y_dev)
    dev_dataset = data(dev_dataset)

    train_loader = DataLoader(train_dataset, batch_size = batch_size, drop_last = True, shuffle = True)
    dev_loader = DataLoader(dev_dataset, batch_size = batch_size, drop_last = True, shuffle = True)
    return train_loader, dev_loader

