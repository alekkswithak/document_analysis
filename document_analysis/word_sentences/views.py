from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Word


class WordListView(ListView):
    model = Word
    queryset = Word.objects.all()
    template_name = 'word_list.html'
    paginate_by = 10
