import os
from flask import Flask, request
import requests
app = Flask(__name__)

import nltk
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer

import re
from collections import Counter
import urllib.request
from bs4 import BeautifulSoup



stemmer = LancasterStemmer()
path = 'data/train.txt'

def open_chats(path):
    lines = open(str(path)).readlines()
    tags = []
    sents = []
    for line in lines:
        tag, sentence = line.split(':')
        tags.append(tag)
        sents.append(sentence[:-1])

    return tags,sents


def pre_process_text(path):
    corpus_words = {}
    class_words = {}
    tags, sents = open_chats(path)
    # turn a list into a set (of unique items) and then a list again (this removes duplicates)
    classes = list(set([temp_tag for temp_tag in tags]))
    for c in classes:
        # prepare a list of words within each class
        class_words[c] = []

    # loop through each sentence in our training data
    for i, temp_sent in enumerate(sents):
        # tokenize each sentence into words
        for word in nltk.word_tokenize(temp_sent):
            # ignore a some things
            if word not in ["?", "'s"]:
                # stem and lowercase each word
                stemmed_word = stemmer.stem(word.lower())
                # have we not seen this word already?
                if stemmed_word not in corpus_words:
                    corpus_words[stemmed_word] = 1
                else:
                    corpus_words[stemmed_word] += 1
                # add the word to our words in class list
                class_words[tags[i]].extend([stemmed_word])

    return corpus_words, class_words


# calculate a score for a given class taking into account word commonality
def calculate_class_score_commonality(sentence, class_name, show_details=True):
    score = 0
    # tokenize each word in our new sentence
    for word in nltk.word_tokenize(sentence):
        # check to see if the stem of the word is in any of our classes
        if stemmer.stem(word.lower()) in class_words[class_name]:
            # treat each word with relative weight
            score += (1 / corpus_words[stemmer.stem(word.lower())])

            if show_details:
                print ("   match: %s (%s)" % (stemmer.stem(word.lower()), 1 / corpus_words[stemmer.stem(word.lower())]))
    return score

# return the class with highest score for sentence
def classify(sentence):
    high_class = None
    high_score = 0
    # loop through our classes
    for c in class_words.keys():
        # calculate score of sentence for each class
        score = calculate_class_score_commonality(sentence, c, show_details=False)
        # keep track of highest score
        if score > high_score:
            high_class = c
            high_score = score

    return high_class, high_score

global corpus_words
global class_words
corpus_words, class_words = pre_process_text(path)

@app.route('/', methods=['GET'])
def index():
    return 'Simple Text Tagger API'

@app.route('/text_tag', methods=['GET'])
def text_tag():
    query = request.args.get('q')
    return classify(query)[0]

@app.route('/text_tag', methods=['PUT'])
def text_tag_input():
    data = request.data
    f = open("data/train.txt",'a')
    f.write(data);
    f.close()
    print("Successful")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host="0.0.0.0", port=port, debug=True)
