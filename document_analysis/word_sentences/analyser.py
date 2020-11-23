import os
import spacy
from collections import defaultdict
from datetime import datetime
from spacy.lang.en.stop_words import STOP_WORDS
from .models import (
    Word,
    Sentence,
    Document,
    DocumentWord
)


class TempWord:
    """
    Temporary container for word data
    """

    def __init__(self):
        self.text = None
        self.sentences = set()
        self.frequency = 0


class TempDoc:
    """
    Temporary container for document data
    """

    def __init__(self):
        self.text = None
        self.sentences = set()
        self.word_frequency = defaultdict(int)


class Analyser:
    """
    Deconstructs documents into words and corresponding sentences.
    Can be run for one document or more, accumulates the results.
    Saves the results to a database.
    """

    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.words = defaultdict(TempWord)
        self.document_data = defaultdict(TempDoc)

    def parse_token(self, token):
        """
        Creates or modifies a TempWord object from a token.
        """
        word = token.lemma_.lower()
        self.words[word].text = word
        self.words[word].frequency += 1
        self.words[word].sentences.add(token.sent.text.strip())
        return self.words[word]

    def parse_sentence(self, sentence):
        """
        Parses sentences, no longer necessary for the scope of this task.
        """
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
        """
        Returns the document text and the name of the file.
        """

        if not os.path.isabs(path):
            path = self.absolute_path(path)
        with open(path, encoding='utf8') as d:
            text = d.read()

        filename = os.path.basename(path)
        return text, filename

    def parse_document(self, path):
        """
        Deconstructs a document into TempWord and TempDoc objects.
        """
        text, filename = self.get_document_data(path)
        doc = self.nlp(text)
        temp_doc = self.document_data[filename]

        for token in doc:
            if token.is_alpha and token.lower_ not in STOP_WORDS:
                temp_word = self.parse_token(token)
                temp_doc.sentences.add(token.sent.text.strip())
                temp_doc.word_frequency[temp_word.text] += 1

    def save_data(self):
        """
        Writes TempWord and TempDoc objects to a db.
        """
        #  create and assign senteces to words:
        for text, word in self.words.items():
            word_record, created = Word.objects.get_or_create(
                text=text
            )
            if created:
                word_record.total_frequency = word.frequency
            else:
                word_record.total_frequency += word.frequency
            word_record.save()
            for sentence_text in word.sentences:
                s, _ = Sentence.objects.get_or_create(
                    text=sentence_text
                )
                s.words.add(word_record)

        #  assign sentences and words to documents:
        for document_name, data in self.document_data.items():
            d = Document.objects.create(
                name=document_name
            )
            for sentence in data.sentences:
                s = Sentence.objects.get(
                    text=sentence
                )
                s.document = d
                s.save()
            for word, frequency in data.word_frequency.items():
                w = Word.objects.get(text=word)
                dw = DocumentWord.objects.create(
                    word=w,
                    document=d,
                    frequency=frequency
                )
