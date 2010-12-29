# -*- coding: iso-8859-1 -*-

import sys,os, shutil, traceback
from datetime import *
sys.path.append("/home/danielfranca/workspace/")
sys.path.append("/home/danielfranca/workspace/tintz/apps")
sys.path.append("/home/danielfranca/workspace/pinax-env/lib/python2.6/site-packages/pinax/apps/")

os.environ['DJANGO_SETTINGS_MODULE'] ='tintz.settings'

from django.core.management import setup_environ
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, get_host
from django.template import RequestContext
from django.db.models import Q
from django.http import Http404
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from publications.models import Publication
from follow.models import FollowAuthor, Update
from follow.models import FollowAuthor
from publications.forms import PublicationUploadForm, PublicationEditForm
from tagging.models import *
from django.http import Http404
from django.conf import settings
import datetime

#import warnings
#warnings.simplefilter('ignore', DeprecationWarning)

import os, datetime, mimetypes
import pdb
import glob
import datetime

from PIL import Image
import UnRAR2
import sys, zipfile, os, os.path
from operator import itemgetter, attrgetter

FULL_VIEW   = 700
SIDE_THUMB  = 64

def create_thumbnail(file_path, file_ext, width=150, height=200, eh_pdf = False, cur_datetime = None):

    file_name = os.path.splitext(file_path)[0]
    file_name = file_name.replace('-','_')

    try:
        thumb = Image.open(file_path)
        if thumb.mode != "RGB":
           thumb = thumb.convert("RGB")
    except IOError, e:
        raise e

    if eh_pdf:
        ind = file_name.find(cur_datetime)
        if ind > 0:
            file_name = file_name[0:ind-1]+file_name[ind+len(cur_datetime):len(file_name)]

    xsize, ysize = thumb.size
    widht_display = width

    if xsize <= width:
       width = xsize

    thumb.thumbnail((width,height),Image.ANTIALIAS)
    thumb.save(''.join([file_name, '_thumb','%03d' % (widht_display), file_ext]))

def from_pdf_file(publication, dirname, file_name, cur_datetime):

    file_name = remove_specialchars(file_name)

    try:
        command = unicode("gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=jpeg -r150 -dTextAlphaBits=4 -sOutputFile=",'utf-8')
        command = command+"\""+dirname+"/"+file_name+"_"+cur_datetime+"_"+"%03d.jpg\" \""+unicode(publication.file_name.path,'utf-8')+"\""

        print "RUN: "+command
        os.system(command.encode('utf-8'))

    except Excetion, e:
        raise e

    #create_thumbnail(dirname+"/"+file_name+"_"+str(cur_datetime)+"_"+"001.jpg",".jpg", eh_pdf=True, cur_datetime=str(cur_datetime))
    create_thumbnail(dirname+"/"+file_name+"_"+cur_datetime+"_001.jpg",".jpg", eh_pdf=True, cur_datetime=cur_datetime)

    listfiles = glob.glob( dirname+"/"+file_name+"_"+cur_datetime+"_*.jpg" )

    pag = 0

    for filename in listfiles:
        try:
            create_thumbnail(filename,".jpg", FULL_VIEW, 1400, eh_pdf=True, cur_datetime=cur_datetime)
            create_thumbnail(filename,".jpg", SIDE_THUMB, 128, eh_pdf=True, cur_datetime=cur_datetime)
        except IOError, e:
            print 'Error creating thumbnail'
            raise e
        pag += 1

    return pag, ".jpg"


def unzip_file_into_dir(file, dir, filename):

    zfobj = zipfile.ZipFile(file)
    pag = 0
    file_ext = ""

    filename = remove_specialchars(filename)

    for name in zfobj.namelist():
        if not name.upper().endswith('JPG') and not name.upper().endswith('GIF')\
        and not name.upper().endswith('PNG'):
            continue

        pag += 1
        if (len(file_ext) == 0):
            file_ext = os.path.splitext(name)[1]

        new_file_name = filename+"_"+"{0:03d}".format(pag) + file_ext
        outfile = open(os.path.join(dir, new_file_name ), 'wb')
        outfile.write(zfobj.read(name))
        outfile.close()

        if pag == 1:
            create_thumbnail(dir+"/"+new_file_name, file_ext)

        try:       
            create_thumbnail(dir+"/"+new_file_name, file_ext, FULL_VIEW, 1400)
            create_thumbnail(dir+"/"+new_file_name, file_ext, SIDE_THUMB, 128)
        except IOError, e:
            print 'Error creating thumbnail'
            raise e

    return pag, file_ext

def unrar_file_into_dir(file, dir, filename_noext):

    print file
    rar_file = UnRAR2.RarFile(file)
    rar_file.extract()
    files_coll = []
    file_ext = ""
    sorted(rar_file.infoiter(),key=attrgetter('filename'))
    for info in rar_file.infoiter():
        if not info.filename.upper().endswith('JPG') and not info.filename.upper().endswith('GIF')\
        and not info.filename.upper().endswith('PNG'):
            continue

        files_coll.append(info.filename)

    files_coll.sort()

    filename_noext = remove_specialchars(filename_noext)

    pag = 0
    for filename in files_coll:
        pag += 1
        if len(file_ext) == 0:
            file_ext = os.path.splitext(filename)[1]

        new_file_name = filename_noext+"_"+"{0:03d}".format(pag) + file_ext

        try:
            shutil.move(filename, dir+"/"+new_file_name)
        except:
            os.remove( filename )
            pass

        if pag == 1:
            create_thumbnail(dir+"/"+new_file_name, file_ext)

        try:        
            create_thumbnail(dir+"/"+new_file_name, file_ext, FULL_VIEW, 1400)
            create_thumbnail(dir+"/"+new_file_name, file_ext, SIDE_THUMB, 128)
        except IOError, e:
            print 'Error creating thumbnail'
            raise e

    return pag, file_ext

def remove_specialchars(file_name):

    try:    
        new_file_name = unicode( file_name.replace('-','_'), 'utf-8')
    except:
        return file_name.replace('-','_')

    return new_file_name

def convert2images(publication):
    file_name, file_ext = os.path.splitext(os.path.basename(publication.file_name.path))
    old_file_ext = file_ext

    #Create directory if it doesnt exist
    dirname = "/home/danielfranca/workspace/tintz/site_media/publications/"+publication.author.__unicode__()
    if not os.path.isdir(dirname):
        os.mkdir(dirname,0666)


    #file_name = unicode(file_name,'utf-8')

    try:    
        file_path = unicode(dirname,'utf-8')+"/"+unicode(file_name,'utf-8')
    except:
        pass

    ##########################################################
    ### Generating images from PDF
    ##########################################################

    pages = 0

    cur_datetime = ""

    if mimetypes.guess_type( publication.file_name.path )[0] == 'application/pdf':
        print "PDF File: "+publication.file_name.path
        try:
           cur_datetime = remove_specialchars( str( datetime.datetime.now() ) )
           file_name = remove_specialchars(file_name)
           pages, file_ext = from_pdf_file(publication, dirname, file_name, cur_datetime)
           file_name = file_name + "_" + cur_datetime
        except Exception, e:
           print 'Error converting from PDF: '
           raise e
    elif publication.file_name.path.endswith('.rar') or publication.file_name.path.endswith('.cbr'):
        print "CBR File: "+publication.file_name.path
        try:
           pages, file_ext = unrar_file_into_dir( publication.file_name.path, dirname, file_name )
        except Exception, e:
           print 'Error converting from CBR: '
           raise e
    elif publication.file_name.path.endswith('.zip') or publication.file_name.path.endswith('.cbz'):
        print "CBZ File: "+publication.file_name.path
        try:
           pages, file_ext = unzip_file_into_dir( publication.file_name.path, dirname, file_name )
        except Exception, e:
           print 'Error converting from ZIP: '
           raise e
    else:
        print "PNG/GIF/Image File: "+publication.file_name.path
        img = Image.open( publication.file_name.path )
        img_strip = ''.join([file_path, '_001',file_ext])
        img.save(img_strip)
        create_thumbnail(img_strip, file_ext, 150, 200)
        create_thumbnail(img_strip, file_ext, FULL_VIEW, 1400)
        create_thumbnail(img_strip, file_ext, SIDE_THUMB, 128)
        pages = 1

    print "Number of pages: "+str(pages)

    print "Extension: "+file_ext

    publication.status = 1
    publication.nr_pages = pages
    publication.images_ext = file_ext

    if old_file_ext == '.pdf':
        ind = file_name.find(cur_datetime)
        if ind > 0:
            file_name = file_name[0:ind-1]+file_name[ind+len(cur_datetime):len(file_name)]

    publication.file_name   = remove_specialchars(file_name)+old_file_ext
    publication.save()
    Update.objects.update_followers(1, publication)

print 'Starting Process Publications - DateTime: '+datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%s')

print 'Searching publication in Status 0'
publications = Publication.objects.filter( status = 0  )

if not publications:
    print 'No publications found'
    quit()

print '******START*******' 

for publication in publications:
    print '\n\nGenerating for: %s ' % publication.title
    exc_type, exc_value, exc_traceback = sys.exc_info()

    try:
       convert2images(publication)
    except:
       print 'Error converting to images - '+publication.title
       traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2, file=sys.stdout)

print '******END*******' 
