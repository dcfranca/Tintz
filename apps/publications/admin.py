from publications.models import PublicationReportAbuse
from django.contrib import admin

class PublicationReportAbuseAdmin(admin.ModelAdmin):
    list_display        = ('publication_title', 'reporter')

    def publication_title(self, obj):
        return '%s' % (obj.publication.title)

admin.site.register(PublicationReportAbuse, PublicationReportAbuseAdmin)