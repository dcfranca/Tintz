import datetime
from haystack import indexes
from haystack import site
from publications.models import Publication

class PublicationIndex(indexes.SearchIndex):
    text        = indexes.CharField(use_template=True, document=True)
    title       = indexes.CharField(model_attr='title')
    author      = indexes.CharField(model_attr='author')
    file_name   = indexes.CharField(model_attr='file_name')
    description = indexes.CharField(model_attr='description')
    tags        = indexes.CharField(model_attr='tags')

    def get_queryset(self):
        return Publication.objects.filter(date_added__lte=datetime.datetime.now())

site.register(Publication, PublicationIndex)


