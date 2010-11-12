# -*- coding: iso-8859-1 -*-
#!python

import sys,os, shutil
from datetime import *
sys.path.append("/Users/danielfranca/Workspace/django/view")
sys.path.append("/Users/danielfranca/Workspace/django/view/tintz/apps")
sys.path.append("/Users/danielfranca/Workspace/django/view//pinax//lib/python2.7/site-packages/pinax/apps/")

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

import warnings
warnings.simplefilter('ignore', DeprecationWarning)

import os, datetime, mimetypes
import pdb
import glob

from PIL import Image
import UnRAR2
import sys, zipfile, os, os.path
from operator import itemgetter, attrgetter

FULL_VIEW   = 700
SIDE_THUMB  = 64

def create_thumbnail(file_path, file_ext, width=150, height=200, eh_pdf = False, cur_datetime = None):
    #import pdb; pdb.set_trace()

    file_name = os.path.splitext(file_path)[0]

    try:
        thumb = Image.open(file_path)
    except IOError:
        return

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

def from_pdf_file(publication, dirname, file_name):


    import datetime

    cur_datetime = datetime.datetime.now()

    file_name = remove_specialchars(file_name)

    command = "gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=jpeg -r150 -dTextAlphaBits=4 -sOutputFile="
    command = command+"\""+dirname+"/"+file_name+"_"+str(cur_datetime)+"_"+"%03d.jpg\" \""+publication.file_name.path+"\""
    print "RUN: "+command

    os.system(command)

    create_thumbnail(dirname+"/"+file_name+"_"+str(cur_datetime)+"_"+"001.jpg",".jpg", eh_pdf=True, cur_datetime=str(cur_datetime))

    listfiles = glob.glob( dirname+"/"+file_name+"_"+str(cur_datetime)+"_*.jpg" )

    pag = 0

    for filename in listfiles:
        create_thumbnail(filename,".jpg", FULL_VIEW, 1400, eh_pdf=True, cur_datetime=str(cur_datetime))
        create_thumbnail(filename,".jpg", SIDE_THUMB, 128, eh_pdf=True, cur_datetime=str(cur_datetime))
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

        create_thumbnail(dir+"/"+new_file_name, file_ext, FULL_VIEW, 1400)
        create_thumbnail(dir+"/"+new_file_name, file_ext, SIDE_THUMB, 128)

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

        create_thumbnail(dir+"/"+new_file_name, file_ext, FULL_VIEW, 1400)
        create_thumbnail(dir+"/"+new_file_name, file_ext, SIDE_THUMB, 128)

    return pag, file_ext

def remove_specialchars(file_name):

    #import pdb; pdb.set_trace()

    new_file_name = ''

    for ch in file_name:
        try:
            if (ord(ch) >= 48 and ord(ch) <= 57) or (ord(ch) >= 65 and ord(ch) <= 90) or (ord(ch) >= 97 and ord(ch) <= 122) or (ch == '_'):
               new_file_name += ch
            else:
               new_file_name += '_'
        except:
            new_file_name += '_'

    return new_file_name


def convert2images(publication):
    file_name, file_ext = os.path.splitext(os.path.basename(publication.file_name.path))
    old_file_ext = file_ext

    #Create directory if it doesnt exist
    dirname = "/Users/danielfranca/Workspace/django/view/tintz/site_media/publications/"+publication.author.__unicode__()
    if not os.path.isdir(dirname):
        os.mkdir(dirname,0666)

    file_path = dirname+"/"+file_name

    ##########################################################
    ### Generating images from PDF
    ##########################################################

    pages = 0

    if mimetypes.guess_type( publication.file_name.path )[0] == 'application/pdf':
        print "Arquivo PDF"
        pages, file_ext = from_pdf_file(publication, dirname, file_name)
    elif publication.file_name.path.endswith('.rar') or publication.file_name.path.endswith('.cbr'):
        print "Arquivo CBR"
        pages, file_ext = unrar_file_into_dir( publication.file_name.path, dirname, file_name )
    elif publication.file_name.path.endswith('.zip') or publication.file_name.path.endswith('.cbz'):
        print "Arquivo CBZ"
        pages, file_ext = unzip_file_into_dir( publication.file_name.path, dirname, file_name )
    else:
        print "Arquivo PNG/GIF/Image"
        img = Image.open( publication.file_name.path )
        img_strip = ''.join([file_path, '_001',file_ext])
        img.save(img_strip)
        create_thumbnail(img_strip, file_ext, 150, 200)
        create_thumbnail(img_strip, file_ext, FULL_VIEW, 1400)
        create_thumbnail(img_strip, file_ext, SIDE_THUMB, 128)
        pages = 1

    print "Numero de paginas: "+str(pages)

    print "Extensao: "+file_ext

    publication.status = 1
    publication.nr_pages = pages
    publication.images_ext = file_ext
    publication.file_name   = remove_specialchars(file_name)+old_file_ext
    publication.save()
    Update.objects.update_followers(1, publication)



print 'Starting Process Publications'

print 'Searching publication in Status 0'
publications = Publication.objects.filter( status = 0  )

if not publications:
    print 'No publications found'
    quit()

for publication in publications:
    print 'Generating for: %s ' % publication.title
    convert2images(publication)
