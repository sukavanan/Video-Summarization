import logging
import torch
import numpy as np
import warnings
from transformers import BertTokenizer, BertModel
from model.config import *
warnings.filterwarnings("ignore")

#tokenizes given text and returns index of those tokens as tensors and the segment id tensors to be used in the BERT model
#returns padded tensors
#tensor shape - (n, pad_len) 
def create_tensors_BERT(text):
    print("Tokenizing text...")
    logging.basicConfig(level = logging.INFO)
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    tokenized_text = [tokenizer.tokenize(x) for x in text]
    tokenized_text = [x + ([pad] * (bert_pad_len - len(x))) for x in tokenized_text]
    indexed_text = [tokenizer.convert_tokens_to_ids(x) for x in tokenized_text]
    segment_ids = [[1] * len(x) for x in tokenized_text]
    torch_idx_text = torch.LongTensor(indexed_text)
    torch_seg_ids = torch.LongTensor(segment_ids)
    return tokenized_text, torch_idx_text, torch_seg_ids 

#takes in the index and segment tensors and returns the bert embeddings as a list
def get_embeddings(torch_idx_text, torch_seg_ids):
    print("Getting Embeddings...")
    model = BertModel.from_pretrained('bert-base-uncased', output_hidden_states = True)
    model.eval()
    torch_idx_text, torch_seg_ids = torch_idx_text.to("cpu"), torch_seg_ids.to("cpu")
    model.to(device)
    with torch.no_grad():
        bert_embeddings = []
        for i in range(len(torch_idx_text)):
            print(i, end = "\r")
            text_temp = torch.unsqueeze(torch_idx_text[i], dim = 0).to(device)
            sgmt_temp = torch.unsqueeze(torch_seg_ids[i], dim = 0).to(device)
            output = model(text_temp, sgmt_temp)
            bert_embeddings.append(output[0])
            del text_temp, sgmt_temp
    del model
    return bert_embeddings

#takes in the tokenized text from the create_tensors and bert_embeddings from the get_embeddings functions
#removes padding and untokenizes the words and averages out the embeddings of words split into different tokens
#returns untokenized sentences and embeddings as lists 
def embeddings_to_words(tokenized_text, embeddings):
    print("Untokenizing text and embeddings...")
    embeddings = [x.cpu().detach().numpy() for x in embeddings]
    embeddings = np.concatenate(embeddings, axis = 0)
    sentences = []
    final_emb = []
    for i in range(len(tokenized_text)):
        txt = tokenized_text[i]
        sub_len = 0
        sent = []
        sub = []
        emb = []
        sub_emb = None
        try:
            idx = txt.index(pad)
        except:
            idx = len(txt)
        for j in range(idx):
            if txt[j].startswith("##"):
                if sub == []:
                    sub.append(sent.pop())
                    emb.pop()
                    sub_emb = embeddings[i][j - 1] + embeddings[i][j]
                    sub.append(txt[j][2:])
                    sub_len = 2
                else:
                    sub.append(txt[j][2:])
                    sub_emb += embeddings[i][j]
                    sub_len += 1
            else:
                if sub != []:
                    sent.append("".join(sub))
                    emb.append(sub_emb / sub_len)
                    sub = []
                    sub_emb = None
                    sub_len = 0
                sent.append(txt[j])
                emb.append(embeddings[i][j])
        sentences.append(sent)
        final_emb.append(emb)
    return sentences, final_emb
