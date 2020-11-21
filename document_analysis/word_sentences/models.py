from django.db import models


class Word(models.Model):
    text = models.CharField(max_length=45, unique=True)
    frequency = models.IntegerField(default=0)

    def __str__(self):
        return self.text

    def documents(self):
        out_str = 'Found in: '
        for d in self.document_set.all():
            out_str += '{}, '.format(d.name)
        return out_str[:-2]


class Sentence(models.Model):
    text = models.TextField(unique=True)
    words = models.ManyToManyField(Word)


class Document(models.Model):
    name = models.CharField(max_length=16)
    words = models.ManyToManyField(Word)

    def __str__(self):
        return self.name

    def word_total(self):
        return len(self.words.all())
