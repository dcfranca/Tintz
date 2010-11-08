from django.utils import simplejson
from dajaxice.core import dajaxice_functions
from dajax.core import Dajax
from publications.models import Publication, PublicationScore
import random
import logging
import pdb
import os, datetime
from tintz import settings
import dajax
import logging
from django.contrib.auth.models import User
from operator import div
from django.template.defaulttags import ifequal
from django.core.urlresolvers import reverse

def set_stars(request, score):

    star_empty = '/site_media/images/star_empty.png'
    star_full  = '/site_media/images/star_full.png'

    dajax = Dajax()

    dajax.assign('#star1','src', star_empty)
    dajax.assign('#star2','src', star_empty)
    dajax.assign('#star3','src', star_empty)
    dajax.assign('#star4','src', star_empty)
    dajax.assign('#star5','src', star_empty)

    cur_star = 1
    logging.debug('Stars - Score: '+str(score))
    while score >= cur_star:
        id_star = '#star'+str(cur_star)
        dajax.assign(id_star,'src', star_full)
        cur_star += 1

    return dajax.json()

dajaxice_functions.register(set_stars)

def vote_star(request, publication_id, score):

    #pdb.set_trace()

    vote_publication(request, publication_id, score)

    return set_stars(request, score)

dajaxice_functions.register(vote_star)

def cur_score(request, publication_id):

  publication = Publication.objects.get(pk=publication_id)

  try:
    publicationScore = PublicationScore.objects.get(  publication=publication, who_vote = request.user )
  except:
    publicationScore  = None

  if publicationScore != None:
     return set_stars(request, publicationScore.rate)
  else:
     return set_stars(request, 0)

dajaxice_functions.register(cur_score)


def vote_publication(request, publication_id, rate):

    #pdb.set_trace()

    publication = Publication.objects.get(pk=publication_id)

    is_voted = False
    try:
        #Check if there's a vote already
        publication_score = PublicationScore.objects.get( publication = publication, who_vote = request.user )
        is_voted = True
    except PublicationScore.DoesNotExist:
        publication_score = PublicationScore()
        publication_score.rate = 0
        is_voted = False

    if not is_voted:
        publication_score.publication = publication
        publication_score.who_vote    = request.user

    publication_score.vote_date   = datetime.datetime.now()
    publication_score.rate        = rate

    publication_score.save()
    publications_scores = PublicationScore.objects.filter( publication = publication )
    total_rates = 0

    if publications_scores.count() > 100:
        for rates in publications_scores:
            total_rates += int(rates.rate)

        publication.rate = str(float((float(total_rates)/publications_scores.count())*20))
        publication.save()

    is_voted = True


def change_page(request, image_file, publication_id, change):

    logging.debug("Change_Page - Inicio")

    publication = Publication.objects.get(pk=publication_id)

    cur_page= int(image_file[len(image_file)-16:len(image_file)-13])
    dajax = Dajax()

    change_page = (cur_page + change)

    if change_page > publication.nr_pages or change_page < 1:
        return dajax.json()


    format_number = '%03d' % (change_page)
    new_page_file = '/site_media/'+publication.get_basename()+'_'+format_number+'_thumb700'+publication.images_ext

    new_page_text = "Pagina %s" % format_number

    dajax = Dajax()
    dajax.assign('#page_publication','src', new_page_file)
    dajax.assign('#page_number_text','innerText', new_page_text)

    logging.debug("Change_Page - Fim")

    return dajax.json()

dajaxice_functions.register(change_page)

def change_to_newpage(request, image_file, publication_id, new_page):

    logging.debug("Change_Page - Inicio")

    publication = Publication.objects.get(pk=publication_id)

    cur_page= int(image_file[len(image_file)-16:len(image_file)-13])
    dajax = Dajax()

    change_page = new_page

    if change_page > publication.nr_pages or change_page < 1:
        return dajax.json()


    format_number = '%03d' % (change_page)
    new_page_file = '/site_media/'+publication.get_basename()+'_'+format_number+'_thumb700'+publication.images_ext

    new_page_text = "Pagina %s" % format_number

    dajax = Dajax()
    dajax.assign('#page_publication','src', new_page_file)
    dajax.assign('#page_number_text','innerText', new_page_text)

    logging.debug("Change_Page - Fim")

    return dajax.json()

dajaxice_functions.register(change_to_newpage)

def more_publications(request, other_user_id, last_publication):
    publications = []

    more_num = 5

    other_user = User.objects.get( pk = other_user_id )
    media_url = '/site_media/'

    last_pub = int(last_publication)

    if other_user == request.user:
        is_me = True
    else:
        is_me = False


    template = """<div class="span-4 publications-cover">
                    <a href="%s">
                    <img src="%s%s" href="%s" alt="%s"/></a>
                  </div>

                  <div class="span-8 list-pub-title">
                    <a href="%s">%s</a>
                  </div>

                  <div class="span-8 last list-pub-description">%s</div>
                  <div class="list-pub-subtitle"> %s </div>
                  """

    if is_me:
        template += """<div class="span-1 list-pub-button"><a href="%s" ><img src="%simages/publication_edit.png" title="Editar Publica&ccedil;&atilde;o"></img></a></div>
                       <div class="span-1 list-pub-button last"><a href="%s" onclick=" ConfirmChoice('%s'); return false;"><img src="%simages/publication_delete.png" title="Excluir Publica&ccedil;&atilde;o"></img></a></div>"""


    if is_me == True:
        publications = Publication.objects.filter( author = other_user )[last_pub:last_pub+more_num]
    else:
        publications = Publication.objects.filter( author = other_user, rated__lte=request.user.get_profile().age )[last_pub:last_pub+more_num]

    htmlOutput = ""

    for publication in publications:
        str_pages = str(publication.nr_pages)
        if publication.nr_pages > 1:
            str_pages += 'P&aacute;ginas'
        else:
            str_pages += 'P&aacute;gina'

        link_details = reverse('publication_details', args=(publication.author,publication.id,))
        link_edit = reverse('edit_publication', args=(publication.id,))
        link_destroy = reverse('destroy_publication', args=(publication.id,))

        if is_me:
            htmlOutput += template % ( link_details, media_url, publication.get_thumbnail150_name(), link_details, publication.title,
            link_details, publication.title, publication.get_small_text(), str_pages, link_edit, media_url, link_destroy, link_destroy ,media_url )
        else:
            htmlOutput += template % ( link_details, media_url, publication.get_thumbnail150_name(), link_details, publication.title,
            link_details, publication.title, publication.get_small_text(), str_pages,  )


    dajax = Dajax()
    dajax.append('#list-publications','innerHTML', htmlOutput)
    dajax.assign('#last_publication','innerText', last_pub+len(publications))

    return dajax.json()


dajaxice_functions.register(more_publications)


