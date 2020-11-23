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
    """
    Tests the Analyser class
    """

    def test_parse_token(self):
        analyser = Analyser()
        nlp = spacy.load('en_core_web_sm')
        doc = nlp("Word.")
        token = doc[0]
        temp_word = analyser.parse_token(token)
        self.assertTrue(isinstance(temp_word, TempWord))
        self.assertEqual(len(analyser.words), 1)
        self.assertTrue("Word." in temp_word.sentences)
        self.assertEqual(temp_word.text, "word")
        self.assertEqual(temp_word.frequency, 1)

    def test_parse_two_different_tokens(self):
        analyser = Analyser()
        nlp = spacy.load('en_core_web_sm')
        doc = nlp("Word second.")
        word = analyser.parse_token(doc[0])
        second = analyser.parse_token(doc[1])
        self.assertEqual(len(analyser.words), 2)
        self.assertTrue("Word second." in word.sentences)
        self.assertEqual(word.text, "word")
        self.assertEqual(word.frequency, 1)
        self.assertTrue("Word second." in second.sentences)
        self.assertEqual(second.text, "second")
        self.assertEqual(second.frequency, 1)

    def test_parse_two_same_tokens(self):
        analyser = Analyser()
        nlp = spacy.load('en_core_web_sm')
        doc = nlp("Word word.")
        analyser.parse_token(doc[0])
        word = analyser.parse_token(doc[1])
        self.assertEqual(len(analyser.words), 1)
        self.assertTrue("Word word." in word.sentences)
        self.assertEqual(word.text, "word")
        self.assertEqual(word.frequency, 2)

    def test_parse_two_different_tokens_same_lemma(self):
        analyser = Analyser()
        nlp = spacy.load('en_core_web_sm')
        doc = nlp("Word words.")
        analyser.parse_token(doc[0])
        word = analyser.parse_token(doc[1])
        self.assertEqual(len(analyser.words), 1)
        self.assertTrue("Word words." in word.sentences)
        self.assertEqual(word.text, "word")
        self.assertEqual(word.frequency, 2)

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
        self.assertEqual(len(analyser.words), 9)
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
        Tests if the word Universe and Universes get reduced to universe
        """
        analyser = Analyser()
        analyser.parse_document('test_docs/universe.txt')
        analyser.parse_document('test_docs/other_people.txt')
        self.assertTrue('universe' in analyser.words)
        universe = analyser.words['universe']
        self.assertEqual(len(universe.sentences), 2)

    def test_analyser_document_sents(self):
        analyser = Analyser()
        analyser.parse_document('test_docs/universe.txt')
        self.assertEqual(
            len(analyser.document_data['universe.txt'].sentences), 2)

    def test_save_data_single_sentence_document(self):
        analyser = Analyser()
        analyser.parse_document('test_docs/garden.txt')
        analyser.save_data()
        word = Word.objects.filter(text='garden').first()
        self.assertEqual(word.total_frequency, 1)
        self.assertEqual(len(word.sentence_set.all()), 1)
        self.assertEqual(len(word.document_set.all()), 1)
        sentence = word.sentence_set.first()
        document = Document.objects.get(name='garden.txt')
        self.assertEqual(sentence.document, document)

    def test_save_data_two_documents(self):
        analyser = Analyser()
        analyser.parse_document('test_docs/universe.txt')
        analyser.parse_document('test_docs/other_people.txt')
        analyser.save_data()
        universe = Word.objects.filter(text='universe').first()
        self.assertEqual(universe.total_frequency, 2)
        self.assertEqual(len(universe.sentence_set.all()), 2)
        self.assertEqual(len(universe.document_set.all()), 2)
        self.assertEqual(len(Document.objects.all()), 2)
        self.assertEqual(len(Sentence.objects.all()), 5)


class TestSpacy(TestCase):
    """
    Exploratory tests.
    Not testing the application logic.
    """

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

    def test_is_alpha(self):
        nlp = spacy.load('en_core_web_sm')
        doc = nlp("1 $6 £9 /n [ b2 , @ /t ")
        tokens = [
            token.lemma_.lower()
            for token in doc
            if token.is_alpha
        ]
        self.assertEqual(len(tokens), 0)

    def test_token(self):
        nlp = spacy.load('en_core_web_sm')
        doc = nlp("This is a sentence")
        token = doc[0]
        self.assertEqual(token.sent.text, "This is a sentence")
        self.assertEqual(token.text, "This")
        self.assertEqual(token.lower_, "this")
        self.assertEqual(token.lemma_, "this")


class TestModels(TestCase):

    def test_word_relationships(self):
        w = Word()
        w.save()
        s1 = Sentence(text='one')
        s1.save()
        s1.words.add(w)
        s2 = Sentence(text='two')
        s2.save()
        w.sentence_set.add(s2)
        d = Document()
        d.save()
        d.words.add(w)
        self.assertEqual(len(w.sentence_set.all()), 2)
        self.assertEqual(len(w.document_set.all()), 1)
