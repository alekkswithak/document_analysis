import os
from django.core.management import BaseCommand
from document_analysis import settings
from word_sentences.analyser import Analyser


class Command(BaseCommand):
    def handle(self, **kwargs):
        analyser = Analyser()
        path = settings.BASE_DIR.name + '/eigen_test_docs/'
        full_path = os.path.abspath(path)
        for filename in os.listdir(full_path):
            path = os.path.join(full_path, filename)
            assert os.path.isabs(path)
            analyser.parse_document(path)
            self.stdout.write('File "%s" processed.' % (filename))
        self.stdout.write('Setup complete!')