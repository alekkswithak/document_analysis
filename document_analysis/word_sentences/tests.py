from django.test import TestCase
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS
from .models import (
    Word,
    Sentence,
    Document
)


class TestSpacy(TestCase):
    """Exploratory tests"""

    def test_sentence_tokenization(self):
        nlp = English()
        nlp.add_pipe(nlp.create_pipe('sentencizer'))
        doc = nlp("This a sentence. This is another one.")
        sentences = [sent.text for sent in doc.sents]
        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0], "This a sentence.")

    def test_word_tokenization(self):
        nlp = English()
        doc = nlp("This is a single sentence.")
        tokens = [token.text for token in doc if not token.is_punct]
        self.assertEqual(len(tokens), 5)

    def test_word_tokenization_with_stopwords(self):
        nlp = English()
        doc = nlp("This is a single sentence.")
        tokens = [
            token.text
            for token in doc
            if not token.is_punct
            if token.text.lower() not in STOP_WORDS
        ]
        self.assertEqual(len(tokens), 2)


class TestModels(TestCase):

    def test_create(self):
        w = Word()
        w.save()
        Sentence(word=w).save()
        Sentence(word=w).save()
        Document(word=w).save()
        self.assertEqual(len(w.sentence_set.all()), 2)
        self.assertEqual(len(w.document_set.all()), 1)
