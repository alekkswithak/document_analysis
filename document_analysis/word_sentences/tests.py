import os
from django.test import TestCase
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS
from .models import (
    Word,
    Sentence,
    Document
)
from .analyser import Analyser


class AnalyserTests(TestCase):

    def test_get_existing_word(self):
        analyser = Analyser()
        word = Word(text='test')
        word.save()
        returned = analyser.get_word('test')
        self.assertEqual(returned, word)

    def test_get_new_word(self):
        analyser = Analyser()
        returned = analyser.get_word('test')
        self.assertEqual(returned.text, 'test')

    def test_parse_sentence(self):
        analyser = Analyser()
        analyser.parse_sentence('Raccoon dog.')
        raccoon = Word.objects.filter(text='raccoon').first()
        dog = Word.objects.filter(text='dog').first()
        sentence = Sentence.objects.filter(text='Raccoon dog.').first()
        self.assertTrue(sentence in raccoon.sentence_set.all())
        self.assertTrue(sentence in dog.sentence_set.all())
        self.assertTrue(all(w in sentence.words.all() for w in (raccoon, dog)))
        self.assertEqual(len(Word.objects.all()), 2)

    def test_absolute_path(self):
        analyser = Analyser()
        path = 'test_docs/universe.txt'
        returned = analyser.absolute_path(path)
        self.assertTrue(os.path.isabs(returned))

    def test_get_document_data(self):
        analyser = Analyser()
        path = 'test_docs/universe.txt'
        text, filename = analyser.get_document_data(path)
        self.assertTrue('Universe' in text)
        self.assertEqual(filename, 'universe.txt')

    def test_parse_document(self):
        analyser = Analyser()
        path = 'test_docs/universe.txt'
        words = analyser.parse_document(path)
        self.assertEqual(len(words), 10)
        sentences = Sentence.objects.all()
        self.assertEqual(len(sentences), 2)
        documents = Document.objects.all()
        self.assertEqual(len(documents), 1)



class TestSpacy(TestCase):
    """Exploratory tests"""

    def test_sentence_tokenization(self):
        nlp = English()
        nlp.add_pipe(nlp.create_pipe('sentencizer'))
        doc = nlp("This is a sentence. This is another one.")
        sentences = [sent.text for sent in doc.sents]
        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0], "This is a sentence.")

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
            and token.text.lower() not in STOP_WORDS
        ]
        self.assertEqual(len(tokens), 2)


class TestModels(TestCase):

    def test_word_relationships(self):
        w = Word()
        w.save()
        s1 = Sentence()
        s1.save()
        s1.words.add(w)
        s2 = Sentence()
        s2.save()
        w.sentence_set.add(s2)
        d = Document()
        d.save()
        d.words.add(w)
        self.assertEqual(len(w.sentence_set.all()), 2)
        self.assertEqual(len(w.document_set.all()), 1)
