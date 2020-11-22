import os
import spacy
from collections import defaultdict
from datetime import datetime
from spacy.lang.en.stop_words import STOP_WORDS
from .models import (
    Word,
    Sentence,
    Document
)


class TempWord:

    def __init__(self):
        self.text = None
        self.sentences = set()
        self.documents = set()
        self.frequency = 0


class Analyser:

    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.words = defaultdict(TempWord)

    def parse_token(self, token):
        """
        Creates or modifies a TempWord object from a token.
        """
        word = token.lemma_.lower()
        self.words[word].text = word
        self.words[word].frequency += 1
        self.words[word].sentences.add(token.sent.text)
        return self.words[word]

    def parse_sentence(self, sentence):
        doc = self.nlp(sentence)
        words = set(
            self.parse_token(token).text
            for token in doc
            if token.is_alpha
            and token.lower_ not in STOP_WORDS
        )
        return words

    def absolute_path(self, relative_path):
        # TODO: put in helpers
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
        doc = self.nlp(text)

        for token in doc:
            if token.is_alpha and token.lower_ not in STOP_WORDS:
                temp_word = self.parse_token(token)
                temp_word.documents.add(filename)

    def save_data(self):
        for text, word in self.words.items():
            word_record, created = Word.objects.get_or_create(
                text=text
            )
            if created:
                word_record.frequency = word.frequency
            else:
                word_record.frequency += word.frequency
            word_record.save()
            for sentence_text in word.sentences:
                s, _ = Sentence.objects.get_or_create(
                    text=sentence_text
                )
                s.words.add(word_record)
            for document_name in word.documents:
                d, _ = Document.objects.get_or_create(
                    name=document_name
                )
                d.words.add(word_record)

