import mwparserfromhell
from nltk.tokenize import sent_tokenize
from nltk.stem import SnowballStemmer
import re

# TODO: english transliteration??
# TODO: check special symbols (&abc; etc)
# TODO: do we really need a wiki parser??
class PartsExtractor:
    def __init__(self):
        self.stemmer_ru = SnowballStemmer("russian", ignore_stopwords=True)
        self.stemmer_en = SnowballStemmer("english", ignore_stopwords=True)

    def extract_sentences(self, src):
        output = mwparserfromhell.parse(src)
        for item in output.ifilter_text():  # type: str
            for part in item.split('\n'):
                trimmed = part.strip().lower()
                if len(trimmed) <= 1:
                    continue

                for sent in sent_tokenize(trimmed):
                    yield sent

    def extract_words(self, sentences):
        for sent in sentences:
            for word in re.findall('[\w\-]+', sent):
                yield word

    def _stem(self, s):
        if len(s) == len(s.encode()): #ascii
            return self.stemmer_en.stem(s)
        else:
            return self.stemmer_ru.stem(s)

    def extract_words_stemmed(self, sentences):
        for sent in sentences:
            for word in re.findall('[\w\-]+', sent):
                stemmed = self._stem(word)
                if stemmed:
                    yield stemmed

    def extract_bigrams(self, sentences):
        for sent in sentences:
            prev_word = None
            for word in re.findall('[\w\-]+', sent):
                yield word
                if prev_word is not None:
                    yield prev_word + " " + word

                prev_word = word

    def extract_bigrams_stemmed(self, sentences):
        for sent in sentences:
            prev_word = None
            for word in re.findall('[\w\-]+', sent):
                stemmed = self._stem(word)

                yield stemmed
                if prev_word is not None:
                    yield prev_word + " " + stemmed

                prev_word = stemmed