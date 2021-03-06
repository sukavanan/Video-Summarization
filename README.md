Video Summarization

Lecture videos tend to run the duration of a class, anywhere from 45 minutes to 90 plus minutes. Users are becoming selective of what they see and prefer to know the substance of the content beforehand. It becomes important to convey the content quickly with as little filler content as possible. Summarizing a long sequenced educational video has many applications in scenarios where time is a critical resource. The aim of the project is to deliver the same i.e. the extractive summaries for educational videos.

First, tokenize the words in the document using the BERT tokenizer function. Then we extract the BERT embeddings for the tokens using the pre-trained BERT-base-uncased model. Next, we untokenize the tokens and combine their emebeddings. Finally we reduce the dimension of the embeddings using PCA. Along with this the words in the document are labelled 0/1 marking their presence in the extractive summary. The embeddings along with the labels are used as input and output data for the bi-LSTM model.

Dataset Used:

1. TVSum50 - a curated collection of human annotated videos (50 videos chosen from YouTube with varying lengths)
2. DebateSum - consists of 187,386 unique pieces of evidence with corresponding argument and extractive summaries

Steps to regenerate the summaries:

Step 1: Create a virtual environment and load it.

Step 2: install the dependencies from requirements file present in the src folder.
pip install -r requirements.txt

Step 3: Run the loader.py file in the src folder to use the trained model and generate the summaries.
python loader.py

Step 4: Finally, run the code present in the Generate_Results.ipynb to generate the plots showing which parts of the video has been selected.