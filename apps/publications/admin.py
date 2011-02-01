from publications.models import Publication, PublicationReportAbuse
from django.contrib import admin

class PublicationReportAbuseAdmin(admin.ModelAdmin):
    list_display        = ('publication_title', 'reporter')

    def publication_title(self, obj):
        return '%s' % (obj.publication.title)

class PublicationAdmin(admin.ModelAdmin):
    list_display        = ('publication_title','publication_author')

    def publication_title(self, obj):
        return '%s' % (obj.title)

    def publication_author(self, obj):
        return '%s' % (obj.author)

admin.site.register(PublicationReportAbuse, PublicationReportAbuseAdmin)

admin.site.register(Publication, PublicationAdmin)