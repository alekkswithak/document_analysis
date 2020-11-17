from django.test import TestCase
from .models import (
    Word,
    Sentence,
    Document
)


class TestModels(TestCase):

    def test_create(self):
        w = Word()
        w.save()
        Sentence(word=w).save()
        Sentence(word=w).save()
        Document(word=w).save()
        self.assertEqual(len(w.sentence_set.all()), 2)
        self.assertEqual(len(w.document_set.all()), 1)
