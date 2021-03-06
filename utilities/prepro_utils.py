import argparse
import pickle
import numpy as np
from nltk.tokenize import word_tokenize
import nltk

def replace_NNP(txt):
    tagged_tokens = nltk.pos_tag(txt)
    output = []
    proper_nouns = []
    for i,w in enumerate(txt):
        if tagged_tokens[i] == 'NNP':
            output.append('UNK')
            proper_nouns.append(w)
        else:
            output.append(w)
    return output, proper_nouns

def prepro_parser(maxlen, batch_size):
    parser = argparse.ArgumentParser()

    # input and output jsons and h5 on terminal (defining the params)
    parser.add_argument('--input_train_json5', default='./data/quora_raw_train.json', help='input json file to process into hdf5')
    parser.add_argument('--input_test_json5', default='./data/quora_raw_test.json', help='input json file to process into hdf5')
    parser.add_argument('--output_json', default='./data/quora_data_prepro.json', help='output json file')
    parser.add_argument('--output_h5', default='./data/quora_data_prepro.h5', help='output h5 file')
    # parser.add_argument('--num_ans', default=1000, type=int, help='number of top answers for the final classifications.')

    # Parameters
    parser.add_argument('--max_length', default = maxlen, type=int, help='max length of a question, in number of words.')
    parser.add_argument('--word_count_threshold', default=0, type=int, help='only words that occur more than this number of times will be put in vocab')
    parser.add_argument('--token_method', default='nltk', help='tokenization method.')    
    parser.add_argument('--batch_size', default=batch_size, type=int)
    # parser.add_argument('--num_test', default=0, type=int, help='number of test images (to withold until very very end)')

    return parser

def prepro_input(input_sent, max_len = 26):
    vocab = {}

    with open('vocab.txt', 'rb') as vocab_open:
        vocab = pickle.load(vocab_open)
        vocab_open.close()
    itow = {i+1:w for i,w in enumerate(vocab)} # 1-indexed vocab translation table
    wtoi = {w:i+1 for i,w in enumerate(vocab)} # Bag of words model
    if 0 not in itow:
        itow[0] = 'UNK'

    dict_len = len(itow)
    EOS, PAD, SOS = dict_len, dict_len + 1, dict_len +2
    itow[EOS] = '<EOS>'
    itow[SOS] = '<SOS>'
    itow[PAD] = '<PAD>'

    wtoi['<EOS>'] = EOS
    wtoi['<SOS>'] = SOS
    wtoi['<PAD>'] = PAD
    sent = word_tokenize(input_sent)
    sent_len  = len(sent)
    sent, pn = replace_NNP(sent)
    print('sentence', sent)
    n = len(sent)
    print('pn: ', pn)

    for i,word in enumerate(sent):
        sent[i] = (word if word in vocab else 'UNK')

    input_array = np.zeros(max_len, dtype = 'uint32')
    for i, word in enumerate(sent):
        if i< max_len:
            input_array[i] = wtoi[word]

    return input_array, wtoi, itow, pn, sent_len
