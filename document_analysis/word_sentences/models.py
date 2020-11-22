from django.db import models


class Word(models.Model):
    text = models.CharField(max_length=45, unique=True)
    total_frequency = models.IntegerField(default=0)

    def __str__(self):
        return self.text

    def documents(self):
        out_str = 'Found in: '
        for d in self.document_set.all():
            out_str += '{}, '.format(d.name)
        return out_str[:-2]


class Document(models.Model):
    name = models.CharField(max_length=16)
    words = models.ManyToManyField(Word, through='DocumentWord')

    def __str__(self):
        return self.name

    def word_total(self):
        return len(self.words.all())


class DocumentWord(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        null=True
    )
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        null=True
    )
    frequency = models.IntegerField(default=0)


class Sentence(models.Model):
    text = models.TextField(unique=True)
    words = models.ManyToManyField(Word)
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        null=True
    )
