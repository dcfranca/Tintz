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
from follow.models import FollowAuthor
from publications.forms import PublicationUploadForm, PublicationEditForm
from tagging.models import *
from django.http import Http404
from django.conf import settings

import warnings
warnings.simplefilter('ignore', DeprecationWarning)

import os, datetime, mimetypes
import pdb

from PIL import Image
import UnRAR2
import sys, zipfile, os, os.path
from operator import itemgetter, attrgetter

def from_pdf_file(publication, dirname, file_name):
    command = "gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=jpeg -r150 -dTextAlphaBits=4 -sOutputFile="
    command = command+"\""+dirname+"/"+file_name+"_"+"%000d.jpg \" \""+publication.file_name.path+"\""
    print command
        
    os.system(command)

def unzip_file_into_dir(file, dir, filename):
    pdb.set_trace()
    zfobj = zipfile.ZipFile(file)
    pag = 1
    file_ext = ""
    
    for name in zfobj.namelist():
        if name.endswith('/'):
            continue
        if (len(file_ext) == 0):
            file_ext = os.path.splitext(name)[1]
        new_file_name = filename+"_"+"{0:03d}".format(pag) + file_ext
        outfile = open(os.path.join(dir, new_file_name ), 'wb')
        outfile.write(zfobj.read(name))
        outfile.close()
        pag += 1

def unrar_file_into_dir(file, dir, filename_noext):
    pdb.set_trace()
    print file
    rar_file = UnRAR2.RarFile(file)
    rar_file.extract()
    files_coll = []
    file_ext = ""
    sorted(rar_file.infoiter(),key=attrgetter('filename'))
    for info in rar_file.infoiter():
        if info.filename.endswith('/'):
            continue        
        files_coll.append(info.filename)
        
    files_coll.sort()
        
    pag = 1
    for filename in files_coll:
        if len(file_ext) == 0:
            file_ext = os.path.splitext(filename)[1]
        new_file_name = filename_noext+"_"+"{0:03d}".format(pag) + file_ext
        
        try:
            shutil.move(filename, dir+"/"+new_file_name)
        except:
            os.remove( filename )
            pass
        pag += 1


def convert2images(publication):
    file_name, file_ext = os.path.splitext(os.path.basename(publication.file_name.path))
    
    #Create directory if it doesnt exist
    dirname = "/Users/danielfranca/Workspace/django/view/tintz/site_media/publications/"+publication.author.__unicode__()
    if not os.path.isdir(dirname):
        os.mkdir(dirname,0666)

    file_path = dirname+"/"+file_name

    ##########################################################
    ### Generating images from PDF
    ##########################################################    

    #If it's an image doesn't need to convert
    print 'MimeType: %s' % mimetypes.guess_type( publication.file_name.path )[0]
    if mimetypes.guess_type( publication.file_name.path )[0] == 'application/pdf':
        print "Arquivo PDF"
        from_pdf()
    elif publication.file_name.path.endswith('.rar') or publication.file_name.path.endswith('.cbr'):
        print "Arquivo CBR"
        unrar_file_into_dir( publication.file_name.path, dirname, file_name )
    elif publication.file_name.path.endswith('.zip') or publication.file_name.path.endswith('.cbz'):
        print "Arquivo CBZ"
        #unzip_file_into_dir( publication.file_name.path, dirname, file_name )
        
    else:
        print "Arquivo PNG/GIF/Image"
        """
        doc = gfx.open("pdf",file_path+file_ext)
    
        #Get aspect Ratio
        page1 = doc.getPage(1)
        ratio = 1    

        if page1.height > 1000:
            ratio = float(float(1000)/float(page1.height))		
    
        width  = int(page1.width*ratio)
        height = int(page1.height*ratio)
    
        print 'Total Pag: '+str(doc.pages)
    
        for pagenr in range(1,doc.pages+1):
            print "uploadpublication - page: "+str(pagenr)
            page = doc.getPage(pagenr)            
            txt = page.asImage(width, height)
            img = Image.new(mode='RGB', size=(width, height))
            img.fromstring(data=txt)
            img.save(''.join([file_path, '.', str(pagenr), '.png']))        
            publication.save()
    
            png_cover = file_path+".1.png"	      
    
            thumb = Image.open(png_cover)
            thumb.thumbnail((256,256),Image.ANTIALIAS)
            thumb.save(''.join([file_path, '.thumb256x256.png']))
    
            png_thumb = file_path+".thumb128x128.png"
            thumb.thumbnail((128,128),Image.ANTIALIAS)
            thumb.save(''.join([file_path, '.thumb128x128.png'])) 
    
            png_thumb = file_path+".thumb64x64.png"
            thumb.thumbnail((64,64),Image.ANTIALIAS)
            thumb.save(''.join([file_path, '.thumb64x64.png'])) 
        
        publication.nr_pages = doc.pages        
    publication.status = 1
    publication.save()
    """

print 'Starting Process Publications'

print 'Searching publication in Status 0'
publications = Publication.objects.filter( status = 0  )

if not publications:
    print 'No publications found'
    quit()

for publication in publications:
    print 'Generating for: %s ' % publication.title
    convert2images(publication)
