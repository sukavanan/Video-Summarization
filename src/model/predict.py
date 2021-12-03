import torch
import warnings
import pickle as pkl
import re
from model.data_loader import *
from model.model import *
from model.config import *
from model.misc import *
from model.bert_embeddings import *
warnings.filterwarnings("ignore")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def get_words_from_labels(labels, text, pad_token):
    result_text = []
    for i in range(len(labels)):
        sent = []
        temp_text = text[i].split()
        limit = temp_text.index(pad_token)
        for j in range(limit):
            if labels[i][j] == 1:
                sent.append(temp_text[j])
        result_text.append(sent)
    return result_text

def predict(model, text, x):
    lens = get_lengths(text, "<pad>", True)
    labels = []
    for i in range(len(x)):
        print(i, end = "\r")
        ip = x[i].to(device)
        ip = torch.unsqueeze(ip, 0)
        op = model(ip, torch.Tensor([lens[i]]))
        op = op.view(-1, op.shape[-1])
        _, pred = torch.max(op, 1)
        labels.append(pred.tolist())
    return labels

def video_predictions(sentences, multiple = False):
    lst_sentences = sentences
    document = " ".join(lst_sentences)
    document = document.lower()
    document = re.sub("[^a-zA-Z ]", "", document)
    # document = document.replace("[^a-zA-Z ]", "", regex = True)
    document = " ".join([x for x in document.split() if x not in stop])
    document = re.sub(" +", " ", document)
    print(len(document.split()))
    if len(document.split()) > model_word_limit:
        print("Dividing document...")
        documents = divide_chunks(lst_sentences, model_word_limit)
        print(len(documents))
        overall_result = []
        for i in range(len(documents)):
            print("Chunk", i, ":")
            _, final_result = video_predictions(documents[i], True)
            overall_result = overall_result + final_result
        return lst_sentences, overall_result
    else:
        document = cls + " " + document + " " + sep
        tokenized_text, torch_idx_text, torch_seg_ids = create_tensors_BERT([document])
        bert_embeddings = get_embeddings(torch_idx_text, torch_seg_ids)
        text, bert = embeddings_to_words(tokenized_text, bert_embeddings)
        text = [" ".join(x) for x in text]
        text, bert = prepare_data_for_LSTM(text, None, bert, 251)
        transformed_bert = bert_pca(bert, 251)
        model = bLSTM(input_dim, hidden_dim, linear_dim, output_dim).to(device)
        model.load_state_dict(torch.load('model/model.pt'))
        transformed_bert = torch.FloatTensor(transformed_bert)
        labels = predict(model, text, transformed_bert)
        result_text = get_words_from_labels(labels, text, "<pad>")[0]
        print(result_text)
        final_result = [0] * len(lst_sentences)
        prev_idx = 0
        for x in result_text:
            for i in range(prev_idx, len(lst_sentences)):
                if x in lst_sentences[i]:
                    prev_idx = i
                    final_result[i] += 1
                    break
        final_result = [final_result[i] / len(lst_sentences[i].split()) for i in range(len(final_result))]
    return lst_sentences, final_result
