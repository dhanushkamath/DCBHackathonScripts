import re
from collections import Counter
import urllib.request
from bs4 import BeautifulSoup
from glob import glob
import pickle

# delete the final_dict.pickle in the main directory and specify a new url if required
# correction('<incorrect spelling>') will give the corrected spelling.


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







print(correction('awdhar'))

