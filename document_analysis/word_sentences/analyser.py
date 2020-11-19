import os
from datetime import datetime
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS
from .models import (
    Word,
    Sentence,
    Document
)


class Analyser:

    def __init__(self):
        self.nlp = English()
        self.nlp.add_pipe(self.nlp.create_pipe('sentencizer'))

    def get_word(self, token):
        word = Word.objects.filter(text=token).first()
        if word is None:
            word = Word(text=token)
            word.save()
        return word

    def parse_sentence(self, sentence):
        doc = self.nlp(sentence)
        sentence = Sentence(text=sentence)
        sentence.save()
        tokens = [
            token.text.lower()
            for token in doc
            if not token.is_punct
            and token.text.lower() not in STOP_WORDS
        ]
        words = []
        for token in tokens:
            word = self.get_word(token)
            word.sentence_set.add(sentence)
            words.append(word)
        return words

    def absolute_path(self, relative_path):
        path = os.path.dirname(os.path.abspath(__file__))
        for p in relative_path.split('/'):
            path = os.path.join(path, p)
        return path

    def get_document_data(self, path):
        """Returns the document text and the name of the file"""

        if not os.path.isabs(path):
            path = self.absolute_path(path)
        with open(path, encoding='utf8') as d:
            text = d.read()

        filename = os.path.basename(path)
        return text, filename

    def parse_document(self, path):
        text, filename = self.get_document_data(path)
        document = Document(name=filename)
        document.save()
        doc = self.nlp(text)
        sentences = [sent.text for sent in doc.sents]
        words = []
        for sentence in sentences:
            sentence_words = self.parse_sentence(sentence)
            words.extend(sentence_words)

        for word in words:
            word.document_set.add(document)

        return words


