import csv
import os
from datetime import datetime
from django.views.generic.list import ListView
from .models import (
    Word,
    Document,
    DocumentWord,
)
from django.conf import settings
from django.http import HttpResponse, Http404


class WordListView(ListView):
    model = Word
    template_name = 'word_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['heading'] ='All words'
        return context


class DocumentListView(ListView):
    model = Document
    template_name = 'document_list.html'


class DocumentWordListView(ListView):
    model = DocumentWord
    template_name = 'document_word_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doc = Document.objects.get(id=self.kwargs['doc_id'])
        context['doc_id'] = doc.id
        context['heading'] = 'Words from {}'.format(doc.name)
        return context

    def get_queryset(self):
        return DocumentWord.objects.filter(document__id=self.kwargs['doc_id'])


def download(request, doc_id):
    if doc_id == 0:
        name = 'all_documents_{}.txt'.format(datetime.now())
        out = 'All word data:\n\n'
        for w in Word.objects.all():
            out += w.text + '\n'
            out += str(w.total_frequency) + '\n'
            out += w.documents() + '\n'
            for s in w.sentence_set.all():
                out += s.text.strip() + '\n'
            out += '\n'
    else:
        d = Document.objects.get(id=doc_id)
        out = 'Word data for {}:\n\n'.format(d.name)
        name = 'document_{}_words_{}'.format(d.id, datetime.now())
        for w in DocumentWord.objects.filter(document__id=doc_id):
            out += w.word.text + '\n'
            out += str(w.frequency) + '\n'
            for s in w.word.sentence_set.all():
                if s.document.id == w.document.id:
                    out += s.text.strip() + '\n'
            out += '\n'

    response = HttpResponse(out ,content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(name)
    return response
