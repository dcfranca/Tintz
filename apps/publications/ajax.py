from django.utils import simplejson
from dajaxice.core import dajaxice_functions
from dajax.core import Dajax
from publications.models import Publication, PublicationScore
import random
import logging
import pdb
import os, datetime

def set_stars(request, score):

    star_empty = '/site_media/media/images/star_empty.png'
    star_full  = '/site_media/media/images/star_full.png'

    dajax = Dajax()

    dajax.assign('#star1','src', star_empty)
    dajax.assign('#star2','src', star_empty)
    dajax.assign('#star3','src', star_empty)
    dajax.assign('#star4','src', star_empty)
    dajax.assign('#star5','src', star_empty)

    #pdb.set_trace()

    cur_star = 1
    logging.debug('Stars - Score: '+str(score))
    while score >= cur_star:
        id_star = '#star'+str(cur_star)
        dajax.assign(id_star,'src', star_full)
        cur_star += 1

    #dajax.assign('#star1','src', star_full)
    #dajax.assign('#star2','src', star_full)
    #dajax.assign('#star3','src', star_full)
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

    #request.user.message_set.create(message=_("Voto efetuado com sucesso para '%s'") % publication.title )
    is_voted = True
