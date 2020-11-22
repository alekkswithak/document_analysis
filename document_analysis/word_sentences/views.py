from django.views.generic.list import ListView
from .models import (
    Word,
    Document,
    DocumentWord,
)


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
        context['heading'] = 'Words from {}'.format(doc.name)
        context['doc'] = doc
        return context

    def get_queryset(self):
        return DocumentWord.objects.filter(document__id=self.kwargs['doc_id'])
