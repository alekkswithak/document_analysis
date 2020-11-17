from django.db import models


class Word(models.Model):
    text = models.CharField(max_length=45)
    frequency = models.IntegerField(default=0)

    def __str__(self):
        return self.text


class Sentence(models.Model):
    text = models.TextField()
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        )


class Document(models.Model):
    name = models.CharField(max_length=16)
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        )

    def __str__(self):
        return self.name
