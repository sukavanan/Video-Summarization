from nltk.corpus import stopwords
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
data_path = "data.csv"
labeled_data_path = "labeled_data.csv"
text_pkl = "text.pkl"
labels_pkl = "labels.pkl"
bert_pkl = "bert.pkl"
bert_reduced_pkl = "bert_reduced.pkl"
cls = "[CLS]"
sep = "[SEP]"
pad = "[PAD]"
stop = stopwords.words("english")
word_limit = 350
bert_pad_len = 512
bert_emb_dim = 768
reduced_dim = 100
batch_size = 64
input_dim = 100
hidden_dim = 256
linear_dim = 128
output_dim = 2
model_word_limit = 251
