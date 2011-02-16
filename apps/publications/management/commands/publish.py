from django.core.management.base import BaseCommand, CommandError

from publications.models import Publication
from follow.models import FollowAuthor, Update
from follow.models import FollowAuthor

import sys,os, shutil, traceback, libtintz, datetime

class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    #help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        print 'Starting Process Publications - DateTime: '+datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%s')

        print 'Searching publication in Status 0'
        publications = Publication.objects.filter( status = 0  )

        if not publications:
            print 'No publications found'
            quit()

        print '******START*******'

        for publication in publications:
            print '\n\nGenerating for: %s ' % publication.file_name.path
            exc_type, exc_value, exc_traceback = sys.exc_info()

            old_file_name = publication.file_name.path.strip()

            try:
                ret, pages, new_file_name = libtintz.ConvertToImages(publication.file_name.path.strip())
            except UnicodeEncodeError:
                ret, pages, new_file_name = libtintz.ConvertToImages(publication.file_name.path.strip().encode('utf-8'))

            try:
                if ret:
                    print "\nSaving File: "+new_file_name
                    publication.status = 1
                    publication.nr_pages = pages

                    publication.file_name = new_file_name

                    if new_file_name.find('nsbckn5ut_cbopkliq7h26crf7xkgcuybechflgrwehluhwv8t-e3wffqdv2cepofmatjr3uam1t1ucksbfzvjenocgmupkodx34n66-x.jpg') >= 0:
                        publication.file_name = 'ogaaaeho5amchnoco9knsbckn5ut_cbopkliq7h26crf7xkgcuybechflgrwehluhwv8t-e3wffqdv2cepofmatjr3uam1t1ucksbfzvjenocgmupkodx34n66-x.jpg'

                    publication.images_ext = ".jpg"
                    publication.save()
                    Update.objects.update_followers(1, publication)
                    print "\nStatus Updated to 1"

                else:
                    print "Error Converting to images"
            except:
                print "\n****Error converting, passed****"

        print '******END*******'

