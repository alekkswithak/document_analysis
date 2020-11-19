from django.db import models


class Word(models.Model):
    text = models.CharField(max_length=45, unique=True)
    frequency = models.IntegerField(default=0)

    def __str__(self):
        return self.text


class Sentence(models.Model):
    text = models.TextField()
    words = models.ManyToManyField(Word)


class Document(models.Model):
    name = models.CharField(max_length=16)
    words = models.ManyToManyField(Word)

    def __str__(self):
        return self.name
