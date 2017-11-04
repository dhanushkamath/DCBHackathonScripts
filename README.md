# Python APIs

<b>Custom Autocorrect:</b> Scrape a website and use it as dictionary to check for spellings and suggests correction if wrong or returns the same if already correct

<b>Text Tagger:</b> Classify sentences to classes based on intent

These APIs are built using Flask using additional packages such as NLTK, BS4. They use the routes spell_check/ and  text_tag/ and accept q as the input string.


## Setup
It is suggested that you use virtualenv for local installation of python and preventing version conflicts. Assuming you already have it installed already, run the following commands.

```bash
virtualenv env
source env/bin/activate
```
Install all the required packages using pip

```bash
pip install -r requirements.txt
```

Run the required API

```bash
python <script-name>
```

Currently the APIs are hardcoded to run on localhost:3000. For dev purposed and using multiple APIs this port can be changed as per requirement. 
