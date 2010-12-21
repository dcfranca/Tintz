import datetime
from haystack import indexes
from haystack import site
from profiles.models import Profile

class ProfileIndex(indexes.SearchIndex):
    text       = indexes.CharField(use_template=True, document=True)
    first_name = indexes.CharField(model_attr='first_name')
    last_name  = indexes.CharField(model_attr='last_name')
    about      = indexes.CharField(model_attr='about',null=True, default="")
    interests  = indexes.CharField(model_attr='interests',null=True, default="")

    def get_queryset(self):
        return Profile.objects.all()

site.register(Profile, ProfileIndex)

