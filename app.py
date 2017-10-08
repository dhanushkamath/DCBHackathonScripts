import os
from flask import Flask, request
import requests
app = Flask(__name__)

import nltk
from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer

import re
from collections import Counter
import urllib.request
from bs4 import BeautifulSoup
from glob import glob
import pickle

# SPELL CHECK

def words(text): return re.findall(r'\w+', text.lower())


def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True


def scrape_page(url='http://dcb.innovationhackathon.in/'):
    html = urllib.request.urlopen(url)
    soup = BeautifulSoup(html)
    data = soup.findAll(text=True)
    result = filter(visible, data)
    str1 = ''.join(str(e) for e in list(result))
    str2 = str(str1.split())
    names = re.findall(r'[A-Z][a-z]+|[a-z][a-z]+{1-2}',str2)
    names2=[]
    for name in names:
        if len(name)>2:
            names2.append(name.lower())
    return names2, Counter(names2)

if glob('data/final_dict.pickle'):
    pickle_in = open("data/final_dict.pickle","rb")
    WORDS = pickle.load(pickle_in)
 

else:
    url = 'http://dcb.innovationhackathon.in/'
    _, count2 = scrape_page(url)
    count_extra = Counter({'iot':10,'dcb':30,'linkedin':10})
    WORDS = Counter(words(open('data/big.txt').read()))
    WORDS = WORDS + count2 + count_extra
    pickle_out = open("data/final_dict.pickle","wb")
    pickle.dump(WORDS, pickle_out)
    pickle_out.close()
    


def P(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    return WORDS[word] / N

def correction(word): 
    "Most probable spelling correction for word."
    return max(candidates(word), key=P)

def candidates(word): 
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


# SIMPLE TEXT TAGGER

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


@app.route('/spell_check', methods=['GET'])
def spell_check():
    query = request.args.get('q')
    if correction(query) != query:
      return correction(query)
    else:
      return query 

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
    port = int(os.environ.get('PORT', 33507))
    app.run(host="0.0.0.0", port=port, debug=True)