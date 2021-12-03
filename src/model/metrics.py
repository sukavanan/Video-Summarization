from predict import *
from rouge import Rouge

def create_rouge_data(pred_labels, targ_labels, text):
    pred_text = get_words_from_labels(pred_labels, text)
    targ_text = get_words_from_labels(targ_labels, text)
    pred_sent = [" ".join(x) for x in pred_text]
    targ_sent = [" ".join(x) for x in targ_text]
    return pred_sent, targ_sent

def rouge_score(pred_labels, targ_labels, text):
    hyp, ref = create_rouge_data(pred_labels, targ_labels, text)
    rouge = Rouge()
    scores = rouge.get_scores(hyps = hyp, refs = ref, avg = True)
    return scores
