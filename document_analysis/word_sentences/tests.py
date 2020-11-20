import os
import spacy
from django.test import TestCase
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS
from .models import (
    Word,
    Sentence,
    Document
)
from .analyser import TempWord, Analyser


class AnalyserTests(TestCase):

    def test_store_word(self):
        analyser = Analyser()
        self.assertTrue(isinstance(analyser.words['test'], TempWord))

    def test_parse_sentence(self):
        analyser = Analyser()
        sentence = 'Raccoon dog.'
        analyser.parse_sentence(sentence)
        self.assertTrue('raccoon' in analyser.words)
        raccoon = analyser.words['raccoon']
        self.assertTrue(
            sentence in raccoon.sentences
        )
        self.assertEqual(len(analyser.words), 2)
        self.assertEqual(raccoon.frequency, 1)
        self.assertTrue('dog' in analyser.words)
        dog = analyser.words['dog']
        self.assertTrue(
            sentence in dog.sentences
        )
        self.assertEqual(dog.frequency, 1)

    def test_parse_sentence_two_dogs(self):
        analyser = Analyser()
        sentence = 'Raccoon dog dog.'
        analyser.parse_sentence(sentence)
        self.assertTrue('dog' in analyser.words)
        dog = analyser.words['dog']
        self.assertEqual(dog.frequency, 2)

    def test_parse_sentence_output(self):
        analyser = Analyser()
        sentence = 'Raccoon dog dog.'
        output = analyser.parse_sentence(sentence)
        expected = {'raccoon', 'dog'}
        self.assertEqual(expected, output)

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
        analyser.parse_document(path)
        self.assertEqual(len(analyser.words), 10)
        self.assertTrue('universe' in analyser.words)
        universe = analyser.words['universe']
        self.assertTrue(universe.sentences)

    def test_parse_two_documents(self):
        analyser = Analyser()
        analyser.parse_document('test_docs/universe.txt')
        analyser.parse_document('test_docs/other_people.txt')
        self.assertTrue('people' in analyser.words)
        people = analyser.words['people']
        self.assertEqual(len(people.sentences), 2)

    def test_parse_two_documents_lemmas(self):
        """
        Tests if the word Universe and Universes get reduced to Universe
        """
        analyser = Analyser()
        analyser.parse_document('test_docs/universe.txt')
        analyser.parse_document('test_docs/other_people.txt')
        self.assertTrue('universe' in analyser.words)
        universe = analyser.words['universe']
        self.assertEqual(len(universe.sentences), 2)
        self.assertEqual(len(universe.documents), 2)


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

    def test_word_tokenization_lemma(self):
        nlp = spacy.load('en_core_web_sm')
        doc = nlp("ask asking asks")
        tokens = [
            token.lemma_.lower()
            for token in doc
            if not token.is_punct
            and token.text.lower() not in STOP_WORDS
        ]
        self.assertEqual(len(set(tokens)), 1)


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
